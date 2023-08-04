from collections import namedtuple
from concurrent import futures
from threading import Thread
from time import sleep
from datetime import datetime
from copy import deepcopy
from random import choice
from grpc import server, insecure_channel

from grpc_health.v1 import health
from grpc_health.v1 import health_pb2
from grpc_health.v1 import health_pb2_grpc

import client_pb2_grpc
import backend_pb2_grpc
from message_definitions_pb2 import (SubscribeMessage,
                                     EmptyMessage,
                                     AvailableServices)


subscribers = {}

class AttacksManagerServicer(backend_pb2_grpc.AttacksManagerServicer):
    def subscribe(self, request: SubscribeMessage, context
                  ) -> EmptyMessage:
        global subscribers

        primitive = request.primitive_type
        attack_name = request.attack_name
        service_name = request.service_name
        port = request.port
        description = request.description

        Services = namedtuple("Services",
                              ["service_name", "addresses", "description"])

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

        return EmptyMessage()


class CryptoAttacksServicer(client_pb2_grpc.CryptoAttacksServicer):

    def getAvailableServices(self, request: EmptyMessage, context
                             ) -> AvailableServices:
        available_services = []
        for primitive_type, attacks in subscribers.items():
            for attack in attacks.keys():

                if len(subscribers[primitive_type][attack].addresses) == 0:
                    continue

                address = choice(subscribers[primitive_type][attack].addresses)
                service_info = subscribers[primitive_type][attack]
                available_services.append \
                    (AvailableServices.AvailableService(
                     primitive_type=primitive_type,
                     attack_name=attack,
                     address=address,
                     service_name=service_info.service_name,
                     description=service_info.description))


        resp = AvailableServices(
                services=available_services)
        return resp


def remove_subscriber(primitive_type: int, attack_name: str, address: str,
                      subscribers
                      ) -> None:
    services = subscribers[primitive_type][attack_name]
    if address in services.addresses:
        services.addresses.remove(address)


def perform_healthcheck(address: str, service_name: str, primitive_type: int,
                        attack_name: str, subscribers
                        ) -> None:
    try:
        with insecure_channel(address) as channel:
            health_stub = health_pb2_grpc.HealthStub(channel)
            resp = health_stub.Check(health_pb2.HealthCheckRequest(
                service=service_name))
            if resp.status != health_pb2.HealthCheckResponse.SERVING:
                remove_subscriber(primitive_type, attack_name, address, subscribers)
    except Exception as e:
        print(e)
        remove_subscriber(primitive_type, attack_name, address, subscribers)


def healthcheck() -> None:
    global subscribers
    new_subscribers = deepcopy(subscribers)
    for primitive_type, attacks in subscribers.items():
        for attack_name in attacks.keys():
            service_name = subscribers[primitive_type][attack_name].service_name
            addresses = subscribers[primitive_type][attack_name].addresses
            for address in addresses:
                perform_healthcheck(address, service_name, primitive_type,
                                    attack_name, new_subscribers)
    print(f"{datetime.now()}: {subscribers}")
    subscribers = new_subscribers


def healthcheck_wrapper(sleep_timeout: float) -> None:
    while True:
        healthcheck()
        sleep(sleep_timeout)


class Backend:

    def __init__(self, address: str):
        grpc_server = server(futures.ThreadPoolExecutor(max_workers=10))

        backend_pb2_grpc.add_AttacksManagerServicer_to_server(
                AttacksManagerServicer(), grpc_server)
        client_pb2_grpc.add_CryptoAttacksServicer_to_server(
            CryptoAttacksServicer(), grpc_server)

        grpc_server.add_insecure_port(address)

        # Use a daemon thread to toggle health status
        healthcheck_thread = Thread(
            target=healthcheck_wrapper,
            args=(5,),
            daemon=True,
        )
        healthcheck_thread.start()

        grpc_server.start()
        grpc_server.wait_for_termination()


Backend('0.0.0.0:50051')
