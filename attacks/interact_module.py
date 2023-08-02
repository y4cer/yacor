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

from ecdsa_reused_nonce.attack import attack


class DigitalSignatureAttackServicer(
        attack_service_api_pb2_grpc.DigitalSignatureAttackServiceServicer):

    def ecdsaReusedNonceAttack(self, request, context):
        data = {
            "pubkey_order": bytes_to_long(request.pubkey_order),
            "sig1": request.signature1,
            "sig2": request.signature2,
            "msg_hash1": request.msg_hash1,
            "msg_hash2": request.msg_hash2
        }
        recovered_key = attack(**data)

        print(f"Recovered private key: {recovered_key}")
        resp = message_definitions_pb2.ReusedNonceAttackResponse(
                private_key=long_to_bytes(recovered_key))
        return resp


def inform_backend(service_name):
    with grpc.insecure_channel("backend:50051") as channel:
        attack_manager_stub = backend_api_pb2_grpc.AttacksManagerServiceStub(channel)
        subscription_args = message_definitions_pb2.SubscribeMessage(
                primitive_type=message_definitions_pb2.PRIMITIVE_TYPE_DIGITAL_SIGNATURE,
                attack_name="ECDSA Reused Nonce attack",
                port=50052,
                service_name=service_name
                )
        attack_manager_stub.subscribe(subscription_args)

def _configure_health_server(server: grpc.Server, service):
    health_servicer = health.HealthServicer(
        experimental_non_blocking=True,
        experimental_thread_pool=futures.ThreadPoolExecutor(max_workers=10),
    )
    health_pb2_grpc.add_HealthServicer_to_server(health_servicer, server)
    health_servicer.set(service, health_pb2.HealthCheckResponse.SERVING)


if __name__ == '__main__':
    try:
        service_name = "attack_service_api.DigitalSignatureAttackService"
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

        attack_service_api_pb2_grpc.add_DigitalSignatureAttackServiceServicer_to_server(
                DigitalSignatureAttackServicer(), server)
        server.add_insecure_port("0.0.0.0:50052")
        _configure_health_server(server, service_name)
        server.start()

        inform_backend(service_name)

        server.wait_for_termination()

    except KeyboardInterrupt:
        print('\nInterrupted')
        exit(0)
