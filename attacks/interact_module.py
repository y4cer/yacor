from concurrent import futures
from Crypto.Util.number import bytes_to_long, long_to_bytes
import grpc
import threading
from time import sleep

import attack_service_api_pb2
import attack_service_api_pb2_grpc
import backend_api_pb2
import backend_api_pb2_grpc
import message_definitions_pb2

from grpc_health.v1 import health
from grpc_health.v1 import health_pb2
from grpc_health.v1 import health_pb2_grpc
from grpc_reflection.v1alpha import reflection

def inform_backend(service_name, description, port, primitive_type, attack_name):
    with grpc.insecure_channel("backend:50051") as channel:
        attack_manager_stub = backend_api_pb2_grpc.AttacksManagerServiceStub(channel)
        subscription_args = message_definitions_pb2.SubscribeMessage(
                primitive_type=primitive_type,
                attack_name=attack_name,
                port=port,
                service_name=service_name,
                description=description,
                )
        attack_manager_stub.subscribe(subscription_args)

def configure_health_server(server: grpc.Server, service):
    health_servicer = health.HealthServicer(
        experimental_non_blocking=True,
        experimental_thread_pool=futures.ThreadPoolExecutor(max_workers=10),
    )
    health_pb2_grpc.add_HealthServicer_to_server(health_servicer, server)
    health_servicer.set(service, health_pb2.HealthCheckResponse.SERVING)


if __name__ == '__main__':
    try:
        package_name = "attack_service_api"
        service_name = "DigitalSignatureAttackService"
        proto_name = "attack_service_api"
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

        attack_service_api_pb2_grpc.add_DigitalSignatureAttackServiceServicer_to_server(
                DigitalSignatureAttackServicer(), server)
        server.add_insecure_port("0.0.0.0:50052")

        configure_health_server(server, service_name)

        SERVICE_NAMES = (
            attack_service_api_pb2.DESCRIPTOR.services_by_name['DigitalSignatureAttackService'].full_name,
            reflection.SERVICE_NAME,
        )
        reflection.enable_server_reflection(SERVICE_NAMES, server)

        server.start()

        inform_backend(service_name, proto_name, package_name)

        server.wait_for_termination()

    except KeyboardInterrupt:
        print('\nInterrupted')
        exit(0)
