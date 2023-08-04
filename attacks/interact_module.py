"""Вспомогательный модуль, содержащий функции для инициализации сервисов"""

from concurrent import futures
from grpc import insecure_channel, Server

import backend_pb2_grpc
from message_definitions_pb2 import PrimitiveType, SubscribeMessage

from grpc_health.v1 import health
from grpc_health.v1 import health_pb2
from grpc_health.v1 import health_pb2_grpc

def inform_backend(
        service_name: str,
        description: str,
        port: int,
        primitive_type: PrimitiveType,
        attack_name: str
) -> None:
    with insecure_channel("backend:50051") as channel:
        attack_manager_stub = backend_pb2_grpc.AttacksManagerStub(channel)
        subscription_args = SubscribeMessage(
                primitive_type=primitive_type,
                attack_name=attack_name,
                port=port,
                service_name=service_name,
                description=description,
                )
        attack_manager_stub.subscribe(subscription_args)

def configure_health_server(server: Server, service: str) -> None:
    health_servicer = health.HealthServicer(
        experimental_non_blocking=True,
        experimental_thread_pool=futures.ThreadPoolExecutor(max_workers=10),
    )
    health_pb2_grpc.add_HealthServicer_to_server(health_servicer, server)
    health_servicer.set(service, health_pb2.HealthCheckResponse.SERVING)
