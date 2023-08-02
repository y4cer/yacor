from concurrent import futures
from Crypto.Util.number import bytes_to_long, long_to_bytes
import grpc

import attack_service_api_pb2
import attack_service_api_pb2_grpc
import backend_api_pb2
import backend_api_pb2_grpc
import message_definitions_pb2

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


def inform_backend():
    with grpc.insecure_channel("localhost:50051") as channel:
        attack_manager_stub = backend_api_pb2_grpc.AttacksManagerServiceStub(channel)
        subscription_args = message_definitions_pb2.SubscribeMessage(
                primitive_type=message_definitions_pb2.PRIMITIVE_TYPE_DIGITAL_SIGNATURE,
                attack_name="ECDSA Reused Nonce attack"
                )
        attack_manager_stub.subscribe(subscription_args)


if __name__ == '__main__':
    try:
        inform_backend()

        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

        attack_service_api_pb2_grpc.add_DigitalSignatureAttackServiceServicer_to_server(
                DigitalSignatureAttackServicer(), server)

        server.add_insecure_port("0.0.0.0:50052")
        server.start()
        server.wait_for_termination()
    except KeyboardInterrupt:
        print('\nInterrupted')
        exit(0)
