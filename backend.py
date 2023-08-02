from concurrent import futures
import grpc

# import gen.client_api_pb2 as client_api_pb2_
import client_api_pb2_grpc
# import gen.backend_api_pb2 as backend_api_pb2_
import backend_api_pb2_grpc
import attack_service_api_pb2_grpc
import message_definitions_pb2

subscribers = {}

class AttacksManagerServicer(backend_api_pb2_grpc.AttacksManagerServiceServicer):
    #TODO: unsibscribe
    def subscribe(self, request, context):
        global subscribers

        print(request.primitive_type)
        print(request.attack_name)

        primitive = request.primitive_type
        attack_name = request.attack_name
        if primitive not in subscribers:
            metadata = {
                request.attack_name: []
            }
            subscribers[primitive] = metadata

        subscribers[primitive][attack_name].append(context.peer())

        return message_definitions_pb2.EmptyMessage()

class CryptoAttacksServicer(client_api_pb2_grpc.CryptoAttacksServiceServicer):

    def getAvailableServices(self, request, context):

        for k, v in subscribers.items():
            print(k, v.keys())

        resp = message_definitions_pb2.AvailableServices(entries=
                [message_definitions_pb2.MapFieldEntry(
                    key="digital_signatures", value="ecdsa nonce reuse attack"
                    )])
        return resp

class DigitalSignatureAttackServicer(
        client_api_pb2_grpc.DigitalSignatureAttackServiceServicer):

    def __init__(self) -> None:
        super().__init__()

    def ecdsaReusedNonceAttack(self, request, context: grpc.ServicerContext):
        data = {
            "pubkey_order": request.pubkey_order.hex(),
            "sig1": request.signature1.hex(),
            "sig2": request.signature2.hex(),
            "msg_hash1": request.msg_hash1.hex(),
            "msg_hash2": request.msg_hash2.hex()
        }
        print(f"{data=}")
        # res = (request.pubkey_order,
        #       request.signature1,
        #       request.signature2,
        #       request.msg_hash1,
        #       request.msg_hash2)
        # print(res)
        sub = subscribers[message_definitions_pb2.PRIMITIVE_TYPE_DIGITAL_SIGNATURE]["ECDSA Reused Nonce attack"]
        print(sub)
        resp = None
        with grpc.insecure_channel("127.0.0.1:50052") as channel:
            attack_service_stub = attack_service_api_pb2_grpc.DigitalSignatureAttackServiceStub(channel)
            resp = attack_service_stub.ecdsaReusedNonceAttack(request)

        return resp

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
        server.start()
        server.wait_for_termination()


Backend('127.0.0.1:50051')
print(123)
