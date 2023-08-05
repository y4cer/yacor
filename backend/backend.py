"""Бэкенд модуль. Реализует сервисы для клиента и для атакующих сервисов"""

from concurrent import futures
import collections
import copy
import datetime
import grpc
import random
import threading
import time

from grpc_health.v1 import health_pb2
from grpc_health.v1 import health_pb2_grpc

import backend_pb2_grpc
import client_pb2_grpc
import message_definitions_pb2

subscribers = {}

class AttacksManagerServicer(backend_pb2_grpc.AttacksManagerServicer):
    def subscribe(
            self,
            request: message_definitions_pb2.SubscribeMessage,
            context
    ) -> message_definitions_pb2.EmptyMessage:
        """
        Подписать удаленный сервис атаки на бэкэнд.

        Args:
            request: запрос на подписку.
            context: контекст соединения.
        """
        global subscribers

        primitive = request.primitive_type
        attack_name = request.attack_name
        service_name = request.service_name
        port = request.port
        description = request.description

        Services = collections.namedtuple(
                "Services",
                ["service_name", "addresses", "description"]
        )

        if primitive not in subscribers.keys():
            metadata = {
                request.attack_name: Services(service_name=service_name,
                                              description=description,
                                              addresses=[])
            }
            subscribers[primitive] = metadata

        service_address = ":".join(context.peer().split(":")[:-1] + \
                                [str(port)])
        subscribers[primitive][attack_name].addresses.append(service_address)

        return message_definitions_pb2.EmptyMessage()


class CryptoAttacksServicer(client_pb2_grpc.CryptoAttacksServicer):

    def getAvailableServices(self,
                             request: message_definitions_pb2.EmptyMessage,
                             context
    ) -> message_definitions_pb2.AvailableServices:
        """
        Получить все текущие доступные (работающие и активные) сервисы.

        Args:
            request: запрос на получение информации о сервисах.
            context: контекст соединения.

        Returns:
            Список всех доступных сервисов с их мета-информацией.
        """
        available_services = []
        for primitive_type, attacks in subscribers.items():
            for attack in attacks.keys():

                if len(subscribers[primitive_type][attack].addresses) == 0:
                    continue

                address = random.choice(subscribers[primitive_type][attack].addresses)
                service_info = subscribers[primitive_type][attack]
                available_services.append \
                    (message_definitions_pb2.AvailableServices.AvailableService(
                     primitive_type=primitive_type,
                     attack_name=attack,
                     address=address,
                     service_name=service_info.service_name,
                     description=service_info.description))


        resp = message_definitions_pb2.AvailableServices(
                services=available_services)
        return resp


def _remove_subscriber(
        primitive_type: int,
        attack_name: str,
        address: str,
        subscribers: dict
) -> None:
    services = subscribers[primitive_type][attack_name]
    if address in services.addresses:
        services.addresses.remove(address)


def perform_healthcheck(
        address: str,
        service_name: str,
        primitive_type: int,
        attack_name: str,
        subscribers: dict
) -> None:
    try:
        with grpc.insecure_channel(address) as channel:
            health_stub = health_pb2_grpc.HealthStub(channel)
            resp = health_stub.Check(health_pb2.HealthCheckRequest(
                service=service_name))
            if resp.status != health_pb2.HealthCheckResponse.SERVING:
                _remove_subscriber(primitive_type, attack_name, address, subscribers)
    except Exception as e:
        print(e)
        _remove_subscriber(primitive_type, attack_name, address, subscribers)


def healthcheck() -> None:
    global subscribers
    new_subscribers = copy.deepcopy(subscribers)
    for primitive_type, attacks in subscribers.items():
        for attack_name in attacks.keys():
            service_name = subscribers[primitive_type][attack_name].service_name
            addresses = subscribers[primitive_type][attack_name].addresses
            for address in addresses:
                perform_healthcheck(address, service_name, primitive_type,
                                    attack_name, new_subscribers)
    print(f"{datetime.datetime.now()}: {subscribers}")
    subscribers = new_subscribers


def healthcheck_wrapper(sleep_timeout: float) -> None:
    """
    Проверить состояние (healthcheck) всех подписанных сервисов.

    Пройти через все подписанные сервисы и выполнить healthcheck,
    удалить сервисы, которые не отвечают, из списка подписчиков.
    """
    while True:
        healthcheck()
        time.sleep(sleep_timeout)


class Backend:
    """
    Регистрирует все необходимые сервисы и запускает обслуживание (serving).
    """
    def __init__(self, address: str):
        grpc_server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

        backend_pb2_grpc.add_AttacksManagerServicer_to_server(
                AttacksManagerServicer(), grpc_server)
        client_pb2_grpc.add_CryptoAttacksServicer_to_server(
            CryptoAttacksServicer(), grpc_server)

        grpc_server.add_insecure_port(address)

        # Use a daemon thread to toggle health status
        healthcheck_thread = threading.Thread(
            target=healthcheck_wrapper,
            args=(5,),
            daemon=True,
        )
        healthcheck_thread.start()

        grpc_server.start()
        grpc_server.wait_for_termination()


Backend('0.0.0.0:50051')
