import client_api_pb2_grpc
import client_api_pb2
from grpc import insecure_channel
from Crypto.Util.number import long_to_bytes

from attacks.ecdsa_reused_nonce.attack import generate_vulnerable_data

with insecure_channel('localhost:50051') as channel:
        crypto_attacks_stub = client_api_pb2_grpc.CryptoAttacksServiceStub(channel)
        crypto_attack_args = client_api_pb2.EmptyMessage()
        print(crypto_attacks_stub.getAvailableServices(crypto_attack_args))

        digital_signature_stub = client_api_pb2_grpc.DigitalSignatureAttackServiceStub(channel)
        vuln_data = generate_vulnerable_data("msg1", "msg2")

        pubkey_order = long_to_bytes(int(vuln_data[0]))

        ecdsa_args = client_api_pb2.ReusedNonceAttackRequest(pubkey_order=pubkey_order,
                                                       signature1=vuln_data[1],
                                                       signature2=vuln_data[2],
                                                       msg_hash1=vuln_data[3].encode(),
                                                       msg_hash2=vuln_data[4].encode())
        print(digital_signature_stub.ecdsaReusedNonceAttack(ecdsa_args))
