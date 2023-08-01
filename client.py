import client_api_pb2_grpc
import client_api_pb2
from grpc import insecure_channel

with insecure_channel('localhost:50051') as channel:
        crypto_attacks_stub = client_api_pb2_grpc.CryptoAttacksServiceStub(channel)
        crypto_attack_args = client_api_pb2.EmptyMessage()
        print(crypto_attacks_stub.getAvailableServices(crypto_attack_args))

        digital_signature_stub = client_api_pb2_grpc.DigitalSignatureAttackServiceStub(channel)

        ecdsa_args = client_api_pb2.ReusedNonceAttackRequest(pubkey_order=b"1",
                                                       signature1=b"2",
                                                       signature2=b"3",
                                                       msg_hash1=b"4",
                                                       msg_hash2=b"5")
        print(digital_signature_stub.ecdsaReusedNonceAttack(ecdsa_args))
