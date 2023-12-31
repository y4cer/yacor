"""Helper module containing internal functions for initializing services"""

from concurrent import futures
import grpc
import logging

import backend_pb2_grpc
import message_definitions_pb2

from grpc_health.v1 import health
from grpc_health.v1 import health_pb2
from grpc_health.v1 import health_pb2_grpc

_LOGGER = logging.getLogger(__name__)


def inform_backend(
        service_name: str,
        description: str,
        port: int,
        primitive_type: message_definitions_pb2.PrimitiveType,
        attack_name: str,
        backend_addr: str
) -> None:
    with grpc.insecure_channel(backend_addr) as channel:
        attack_manager_stub = backend_pb2_grpc.AttacksManagerStub(channel)
        subscription_args = message_definitions_pb2.SubscribeMessage(
                primitive_type=primitive_type,
                attack_name=attack_name,
                port=port,
                service_name=service_name,
                description=description,
        )
        attack_manager_stub.subscribe(subscription_args)
        _LOGGER.info(f"Subscribed service with {attack_name} to backend.")


def configure_health_server(server: grpc.Server, service: str) -> None:
    health_servicer = health.HealthServicer(
        experimental_non_blocking=True,
        experimental_thread_pool=futures.ThreadPoolExecutor(max_workers=10),
    )
    health_pb2_grpc.add_HealthServicer_to_server(health_servicer, server)
    health_servicer.set(service, health_pb2.HealthCheckResponse.SERVING)
