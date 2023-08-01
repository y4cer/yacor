from concurrent import futures
import grpc
import client_api_pb2
import client_api_pb2_grpc
from broker import MessageBroker

class CryptoAttacksServicer(client_api_pb2_grpc.CryptoAttacksServiceServicer):

    def getAvailableServices(self, request, context):
        resp = client_api_pb2.AvailableServices(entries=
                [client_api_pb2.MapFieldEntry(
                    key="digital_signatures", value="ecdsa nonce reuse attack"
                    )])
        return resp

class DigitalSignatureAttackServicer(
        client_api_pb2_grpc.DigitalSignatureAttackServiceServicer):

    broker: MessageBroker

    def __init__(self, broker) -> None:
        super().__init__()
        self.broker = broker

    def ecdsaReusedNonceAttack(self, request, context):
        res = (request.pubkey_order,
              request.signature1,
              request.signature2,
              request.msg_hash1,
              request.msg_hash2)
        print(res)
        self.broker.act('digital_signatures.ecdsa_nonce_reuse', *res)
        return super().ecdsaReusedNonceAttack(request, context)

class Backend:

    def __init__(self, address: str):
        self.broker = MessageBroker()

        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

        client_api_pb2_grpc.add_CryptoAttacksServiceServicer_to_server(
            CryptoAttacksServicer(), server)
        client_api_pb2_grpc.add_DigitalSignatureAttackServiceServicer_to_server(
                DigitalSignatureAttackServicer(self.broker), server)

        server.add_insecure_port(address)
        server.start()
        server.wait_for_termination()


Backend('0.0.0.0:50051')
print(123)
