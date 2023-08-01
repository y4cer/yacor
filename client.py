import client_api_pb2_grpc
import client_api_pb2
from grpc import insecure_channel

with insecure_channel('localhost:50051') as channel:
        stub = client_api_pb2_grpc.CryptoAttacksServiceStub(channel)
        args = client_api_pb2.EmptyMessage()
        print(stub.getAvailableServices(args))
