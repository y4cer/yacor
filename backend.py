from collections import namedtuple
from concurrent import futures
import grpc
import threading
from time import sleep
import copy

import client_api_pb2_grpc
import backend_api_pb2_grpc
import attack_service_api_pb2_grpc
import message_definitions_pb2

from grpc_health.v1 import health
from grpc_health.v1 import health_pb2
from grpc_health.v1 import health_pb2_grpc

subscribers = {}

class AttacksManagerServicer(backend_api_pb2_grpc.AttacksManagerServiceServicer):
    #TODO: unsibscribe
    def subscribe(self, request, context):
        global subscribers

        primitive = request.primitive_type
        attack_name = request.attack_name
        service_name = request.service_name

        Services = namedtuple("Services", ["service_name", "addresses"])

        if primitive not in subscribers.keys():
            metadata = {
                request.attack_name: Services(service_name=service_name,
                                              addresses=[])
            }
            subscribers[primitive] = metadata

        service_address = ":".join(context.peer().split(":")[:-1] + \
                                [str(request.port)])
        subscribers[primitive][attack_name].addresses.append(service_address)

        return message_definitions_pb2.EmptyMessage()

class CryptoAttacksServicer(client_api_pb2_grpc.CryptoAttacksServiceServicer):

    def getAvailableServices(self, request, context):
        available_services = []
        for primitive_type, attacks in subscribers.items():
            available_attacks = list(attacks.keys())
            for attack in attacks.keys():
                if len(subscribers[primitive_type][attack].addresses) == 0:
                    continue
                available_services.append(message_definitions_pb2.MapFieldEntry(
                        key=str(primitive_type), value=available_attacks))

        resp = message_definitions_pb2.AvailableServices(
                entries=available_services)
        return resp

class DigitalSignatureAttackServicer(
        client_api_pb2_grpc.DigitalSignatureAttackServiceServicer):

    def __init__(self) -> None:
        super().__init__()

    def ecdsaReusedNonceAttack(self, request, context: grpc.ServicerContext):
        healthcheck()
        data = {
            "pubkey_order": request.pubkey_order.hex(),
            "sig1": request.signature1.hex(),
            "sig2": request.signature2.hex(),
            "msg_hash1": request.msg_hash1.hex(),
            "msg_hash2": request.msg_hash2.hex()
        }
        print(f"{data=}")

        sub = subscribers[message_definitions_pb2.PRIMITIVE_TYPE_DIGITAL_SIGNATURE]["ECDSA Reused Nonce attack"]
        resp = None
        with grpc.insecure_channel(sub.addresses[0]) as channel:
            attack_service_stub = attack_service_api_pb2_grpc.DigitalSignatureAttackServiceStub(channel)
            resp = attack_service_stub.ecdsaReusedNonceAttack(request)

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
            print(f"address {address} is {resp.status}")
            if resp.status != health_pb2.HealthCheckResponse.SERVING:
                remove_subscriber(primitive_type, attack_name, address, subscribers)
    except Exception as _:
        remove_subscriber(primitive_type, attack_name, address, subscribers)


def healthcheck():
    global subscribers
    new_subscribers = copy.deepcopy(subscribers)
    for primitive_type, attacks in subscribers.items():
        for attack_name in attacks.keys():
            service_name, addresses = subscribers[primitive_type][attack_name]
            for address in addresses:
                perform_healthcheck(address, service_name, primitive_type,
                                    attack_name, new_subscribers)
    print(subscribers)
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
        client_api_pb2_grpc.add_DigitalSignatureAttackServiceServicer_to_server(
                DigitalSignatureAttackServicer(), server)

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
