"""Реализует атаку с повторно используемым числом ECDSA, а также gRPC API.

Предоставляет 2 сервиса gRPC API: один для проверки состояния (healthchecking),
а другой реализует бизнес-логику названной выше атаки.
"""

from Crypto.Util import number
from concurrent import futures
from ecdsa import util, numbertheory
import grpc
import logging
import os

import attack_service_pb2_grpc
import message_definitions_pb2

import interact_module

BACKEND_ADDR = os.environ["BACKEND_ADDR"]
_LOGGER = logging.getLogger(__name__)


def attack(
    *, pubkey_order: bytes,
    sig1: bytes,
    sig2: bytes,
    msg_hash1: bytes,
    msg_hash2: bytes
) -> int:
    """
    Атаковать ECDSA с использованием уязвимости повторно используемого числа.

    Args:
        pubkey_order: порядок открытого ключа.
        sig1: первая подпись для рассмотрения.
        sig2: вторая подпись для рассмотрения.
        msg_hash1: хэш первого сообщения для рассмотрения.
        msg_hash2: хэш второго сообщения для рассмотрения.

    Returns:
        Целочисленное значение закрытого ключа.

    Raises:
        ValueError, если подписи не подвержены этой атаке.
    """

    int_pubkey_order = number.bytes_to_long(pubkey_order)
    r1, s1 = util.sigdecode_string(sig1, int_pubkey_order)
    r2, s2 = util.sigdecode_string(sig2, int_pubkey_order)

    L1 = number.bytes_to_long(msg_hash1)
    L2 = number.bytes_to_long(msg_hash2)

    if (r1 != r2):
        raise ValueError("The signature pairs given are not susceptible to "
                                                                "this attack")

    numerator = ((s2 * L1) % int_pubkey_order) - ((s1 * L2) % int_pubkey_order)
    denominator = numbertheory.inverse_mod(
            r1 * ((s1 - s2) % int_pubkey_order),
            int_pubkey_order
    )

    privateKey = numerator * denominator % int_pubkey_order

    return int(privateKey)

class DigitalSignatureAttackServicer(
        attack_service_pb2_grpc.DigitalSignatureAttackServicer):

    def ecdsaReusedNonceAttack(
            self,
            request: message_definitions_pb2.ReusedNonceAttackRequest,
            context
    ) -> message_definitions_pb2.ReusedNonceAttackResponse:
        """
        Реализует бизнес-логику для атаки ECDSA с повторно используемым числом.

        Args:
            request: запрос для атаки.
            context: контекст соединения.

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

        _LOGGER.info(f"Recovered private key: {recovered_key}")
        resp = message_definitions_pb2.ReusedNonceAttackResponse(
                private_key=number.long_to_bytes(recovered_key)
        )

        return resp


def run() -> None:
    service_name = "DigitalSignatureAttackService"
    description = "Service performs nonce reuse attack on ECDSA, utilizing " \
        "the reused `k` in digital signature algorithm generation. Works " \
        "with SHA1"
    port = 50002
    primitive_type = message_definitions_pb2.PRIMITIVE_TYPE_DIGITAL_SIGNATURE

    grpc_server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    attack_service_pb2_grpc.add_DigitalSignatureAttackServicer_to_server(
            DigitalSignatureAttackServicer(),
            grpc_server
    )
    grpc_server.add_insecure_port(f"0.0.0.0:{port}")

    interact_module.configure_health_server(grpc_server, service_name)

    grpc_server.start()

    interact_module.inform_backend(
            service_name,
            description,
            port,
            primitive_type,
            "ECDSA Reused Nonce attack",
            BACKEND_ADDR
    )
    _LOGGER.info("Stared serving")
    grpc_server.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig()
    run()
