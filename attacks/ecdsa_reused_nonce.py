from ecdsa.numbertheory import inverse_mod
from Crypto.Util.number import long_to_bytes, bytes_to_long

from ecdsa import SigningKey, NIST224p
from ecdsa.util import sigdecode_string
from ecdsa.numbertheory import inverse_mod
from hashlib import sha1
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
from grpc_reflection.v1alpha import reflection

from interact_module import inform_backend, configure_health_server

def attack(*, pubkey_order, sig1, sig2, msg_hash1, msg_hash2):
    r1, s1 = sigdecode_string(sig1, pubkey_order)
    r2, s2 = sigdecode_string(sig2, pubkey_order)

    L1 = bytes_to_long(msg_hash1)
    L2 = bytes_to_long(msg_hash2)

    if (r1 != r2):
        raise ValueError("The signature pairs given are not susceptible to this attack")

    numerator = (((s2 * L1) % pubkey_order) - ((s1 * L2) % pubkey_order))
    denominator = inverse_mod(r1 * ((s1 - s2) % pubkey_order), pubkey_order)

    privateKey = numerator * denominator % pubkey_order

    return privateKey

def generate_vulnerable_data(msg1, msg2):

    sk = SigningKey.generate(curve=NIST224p)

    vk = sk.get_verifying_key()

    signature = sk.sign(msg1.encode('utf-8'), k=22)
    signature2 = sk.sign(msg2.encode("utf-8"), k=22)

    msg_hash1 = sha1(msg1.encode('utf-8')).digest()
    msg_hash2 = sha1(msg2.encode('utf-8')).digest()

    return vk.pubkey.order, signature, signature2, msg_hash1, msg_hash2

def ecdsa_reused_nonce_generator():
    vuln_data = generate_vulnerable_data("msg1", "msg2")

    pubkey_order = long_to_bytes(int(vuln_data[0]))

    ecdsa_args = {"pubkey_order": pubkey_order,
                  "signature1": vuln_data[1],
                  "signature2": vuln_data[2],
                  "msg_hash1": vuln_data[3],
                  "msg_hash2": vuln_data[4]
    }
    return ecdsa_args

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


def ecdsa_reused_nonce_handler(message_kwargs, channel):
    digital_signature_stub = attack_service_api_pb2_grpc.DigitalSignatureAttackServiceStub(channel)
    req = message_definitions_pb2.ReusedNonceAttackRequest(**message_kwargs)
    resp = digital_signature_stub.ecdsaReusedNonceAttack(req)
    return resp


def run():
    service_name = "DigitalSignatureAttackService"
    description = """Service performs nonce reuse attack on ECDSA, utilizing the
    reused `k` in digital signature algorithm generation. Works with SHA1"""
    port = 50002
    primitive_type = message_definitions_pb2.PRIMITIVE_TYPE_DIGITAL_SIGNATURE

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    attack_service_api_pb2_grpc.add_DigitalSignatureAttackServiceServicer_to_server(
            DigitalSignatureAttackServicer(), server)
    server.add_insecure_port(f"0.0.0.0:{port}")

    configure_health_server(server, service_name)

    server.start()

    inform_backend(service_name, description, port, primitive_type, "ECDSA Reused Nonce attack")

    server.wait_for_termination()


# For testing
def test():
    msg1 = "message1"
    msg2 = "message2"
    pubkey_order, sig1, sig2, msg_hash1, msg_hash2 = \
            generate_vulnerable_data(msg1, msg2)

    # Start the attack
    attack_params = {
        "pubkey_order": pubkey_order,
        "sig1": sig1,
        "sig2": sig2,
        "msg_hash1": msg_hash1,
        "msg_hash2": msg_hash2
    }
    recovered_sk = attack(**attack_params)
    print(type(recovered_sk))
    print(f"Recovered private key: \t {recovered_sk}")


if __name__ == "__main__":
    run()