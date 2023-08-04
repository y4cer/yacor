"""Implements the ECDSA Reused nonce attack as well as corresponging gRPC API.

Exposes 2 gRPC API services: one for healthchecking, the other one implements
the business logic of the attack mentioned above.
"""

from Crypto.Util.number import long_to_bytes, bytes_to_long
from concurrent import futures
from ecdsa import SigningKey, NIST224p
from ecdsa.numbertheory import inverse_mod
from ecdsa.util import sigdecode_string
from grpc import Channel, server
from hashlib import sha1

import attack_service_pb2_grpc
from message_definitions_pb2 import (ReusedNonceAttackResponse,
                                     ReusedNonceAttackRequest,
                                     PRIMITIVE_TYPE_DIGITAL_SIGNATURE)

from interact_module import inform_backend, configure_health_server

def attack(
    *, pubkey_order: bytes,
    sig1: bytes,
    sig2: bytes,
    msg_hash1: bytes,
    msg_hash2: bytes
) -> int:
    """
    Attack the ECDSA with reused nonce flaw.

    Args:
        pubkey_order: order of the public key.
        sig1: first signature to consider.
        sig2: second signature to consider.
        msg_hash1: hash of the first message to consider.
        msg_hash2: hash of the second message to consider.

    Returns:
        Integer value of the private key.

    Raises:
        ValueError if the signatures are not susceptable to this attack.
    """

    int_pubkey_order = bytes_to_long(pubkey_order)
    r1, s1 = sigdecode_string(sig1, int_pubkey_order)
    r2, s2 = sigdecode_string(sig2, int_pubkey_order)

    L1 = bytes_to_long(msg_hash1)
    L2 = bytes_to_long(msg_hash2)

    if (r1 != r2):
        raise ValueError(
                "The signature pairs given are not susceptible to this attack")

    numerator = (((s2 * L1) % int_pubkey_order) -
                    ((s1 * L2) % int_pubkey_order))
    denominator = inverse_mod(r1 * ((s1 - s2) % int_pubkey_order),
                                                      int_pubkey_order)

    privateKey = numerator * denominator % int_pubkey_order

    return int(privateKey)

def generate_vulnerable_data(
        msg1: str,
        msg2: str,
) -> tuple[bytes, bytes, bytes, bytes, bytes]:
    """
    Generate vulnerable data for the ECDSA Reused Nonce attack.

    Args:
        msg1: first message to weakly sign.
        msg1: second message to weakly sign.

    Returns:
        Tuple with all entries in bytes, containing: order of the public key,
        first signature, second signature, first message hash, second message
        hash.
    """
    sk = SigningKey.generate(curve=NIST224p)

    vk = sk.get_verifying_key()

    signature = sk.sign(msg1.encode('utf-8'), k=42)
    signature2 = sk.sign(msg2.encode("utf-8"), k=42)

    msg_hash1 = sha1(msg1.encode('utf-8')).digest()
    msg_hash2 = sha1(msg2.encode('utf-8')).digest()

    return vk.pubkey.order, signature, signature2, msg_hash1, msg_hash2

def ecdsa_reused_nonce_generator() -> dict[str, bytes]:
    """
    Generate vulnerable data for the ECDSA Reused Nonce attack.

    Returns:
        Kwargs for the ReusedNonceAttackRequest.
    """
    vuln_data = generate_vulnerable_data("msg1", "msg2")

    ecdsa_args = {"pubkey_order": long_to_bytes(int(vuln_data[0])),
                  "signature1": vuln_data[1],
                  "signature2": vuln_data[2],
                  "msg_hash1": vuln_data[3],
                  "msg_hash2": vuln_data[4]
    }
    return ecdsa_args

class DigitalSignatureAttackServicer(
        attack_service_pb2_grpc.DigitalSignatureAttackServicer):

    def ecdsaReusedNonceAttack(
            self,
            request: ReusedNonceAttackRequest,
            context
    ) -> ReusedNonceAttackResponse:
        """
        Implements the business logic for the ECDSA Reused Nonce attack.

        Args:
            request: request for the attack.
            context: connection context.

        Returns:
            ReusedNonceAttackResponse.
        """
        data = {
            "pubkey_order": request.pubkey_order,
            "sig1": request.signature1,
            "sig2": request.signature2,
            "msg_hash1": request.msg_hash1,
            "msg_hash2": request.msg_hash2
        }
        recovered_key = attack(**data)

        print(f"Recovered private key: {recovered_key}")
        resp = ReusedNonceAttackResponse(
                private_key=long_to_bytes(recovered_key))
        return resp


def ecdsa_reused_nonce_handler(
        message_kwargs,
        channel: Channel
) -> ReusedNonceAttackResponse:
    """
    Calls the remote attack service through given channel.

    Args:
        message_kwargs: kwargs for the ReusedNonceAttackRequest.
        channel: transport channel to use.
    """

    digital_signature_stub = \
            attack_service_pb2_grpc.DigitalSignatureAttackStub(channel)
    req = ReusedNonceAttackRequest(**message_kwargs)
    resp = digital_signature_stub.ecdsaReusedNonceAttack(req)
    return resp


def run() -> None:
    service_name = "DigitalSignatureAttackService"
    description = "Service performs nonce reuse attack on ECDSA, utilizing " \
    "the reused `k` in digital signature algorithm generation. Works with SHA1"
    port = 50002
    primitive_type = PRIMITIVE_TYPE_DIGITAL_SIGNATURE

    grpc_server = server(futures.ThreadPoolExecutor(max_workers=10))

    attack_service_pb2_grpc.add_DigitalSignatureAttackServicer_to_server(
            DigitalSignatureAttackServicer(), grpc_server)
    grpc_server.add_insecure_port(f"0.0.0.0:{port}")

    configure_health_server(grpc_server, service_name)

    grpc_server.start()

    inform_backend(service_name, description, port, primitive_type,
                   "ECDSA Reused Nonce attack")

    grpc_server.wait_for_termination()


if __name__ == "__main__":
    run()
