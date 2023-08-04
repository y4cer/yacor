from collections import namedtuple
from concurrent import futures
import grpc
import threading
from time import sleep
import datetime
import copy
from random import choice

import client_api_pb2_grpc
import client_api_pb2
import backend_api_pb2_grpc
import message_definitions_pb2

from grpc_health.v1 import health
from grpc_health.v1 import health_pb2
from grpc_health.v1 import health_pb2_grpc

subscribers = {}

class AttacksManagerServicer(backend_api_pb2_grpc.AttacksManagerServiceServicer):
    def subscribe(self, request, context):
        global subscribers

        primitive = request.primitive_type
        attack_name = request.attack_name
        service_name = request.service_name
        port = request.port
        description = request.description

        Services = namedtuple("Services", ["service_name", "addresses", "description"])

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


class CryptoAttacksServicer(client_api_pb2_grpc.CryptoAttacksServiceServicer):

    def getAvailableServices(self, request, context):
        available_services = []
        for primitive_type, attacks in subscribers.items():
            for attack in attacks.keys():

                if len(subscribers[primitive_type][attack].addresses) == 0:
                    continue

                address = choice(subscribers[primitive_type][attack].addresses)
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


def remove_subscriber(primitive_type, attack_name, address, subscribers):
    services = subscribers[primitive_type][attack_name]
    if address in services.addresses:
        services.addresses.remove(address)


def perform_healthcheck(address, service_name, primitive_type, attack_name, subscribers):
    try:
        with grpc.insecure_channel(address) as channel:
            health_stub = health_pb2_grpc.HealthStub(channel)
            resp = health_stub.Check(health_pb2.HealthCheckRequest(
                service=service_name))
            # print(f"address {address} is {resp.status}")
            if resp.status != health_pb2.HealthCheckResponse.SERVING:
                remove_subscriber(primitive_type, attack_name, address, subscribers)
    except Exception as e:
        print(e)
        remove_subscriber(primitive_type, attack_name, address, subscribers)


def healthcheck():
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


def healthcheck_wrapper(sleep_timeout):
    while True:
        healthcheck()
        sleep(sleep_timeout)


class Backend:

    def __init__(self, address: str):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

        backend_api_pb2_grpc.add_AttacksManagerServiceServicer_to_server(
                AttacksManagerServicer(), server)
        client_api_pb2_grpc.add_CryptoAttacksServiceServicer_to_server(
            CryptoAttacksServicer(), server)

        server.add_insecure_port(address)

        # Use a daemon thread to toggle health status
        healthcheck_thread = threading.Thread(
            target=healthcheck_wrapper,
            args=(5,),
            daemon=True,
        )
        healthcheck_thread.start()

        server.start()
        server.wait_for_termination()


Backend('0.0.0.0:50051')
print(123)
