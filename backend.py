from concurrent import futures
import grpc
import client_api_pb2
import client_api_pb2_grpc

class CryptoAttacksServicer(client_api_pb2_grpc.CryptoAttacksServiceServicer):

    def getAvailableServices(self, request, context):
        resp = client_api_pb2.ExpectedValues(entries=
                [client_api_pb2.MapFieldEntry(key="123", value="asd")]
                )
        return resp

class DigitalSignatureAttackServicer(
        client_api_pb2_grpc.DigitalSignatureAttackServiceServicer):

    def ecdsaReusedNonceAttack(self, request, context):
        return super().ecdsaReusedNonceAttack(request, context)

class Backend:

    def __init__(self, address: str):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

        client_api_pb2_grpc.add_CryptoAttacksServiceServicer_to_server(
            CryptoAttacksServicer(), server)
        client_api_pb2_grpc.add_DigitalSignatureAttackServiceServicer_to_server(
                DigitalSignatureAttackServicer(), server)

        server.add_insecure_port(address)
        server.start()
        server.wait_for_termination()

Backend('0.0.0.0:50051')
