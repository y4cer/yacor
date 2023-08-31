"""Вспомогательный модуль, содержащий функции работы с атакой на ECDSA."""

from Crypto.Util import number
import ecdsa
import grpc
import hashlib

import attack_service_pb2_grpc
import message_definitions_pb2

def generate_vulnerable_data(
        msg1: str,
        msg2: str,
) -> tuple[bytes, bytes, bytes, bytes, bytes]:
    """
    Создать уязвимые данные для атаки ECDSA с повторно используемым числом.

    Args:
        msg1: первое слабо подписываемое сообщение.
        msg2: второе слабо подписываемое сообщение.

    Returns:
        Кортеж с данными в байтах, содержащий: порядок открытого ключа,
        первую подпись, вторую подпись, хэш первого сообщения, хэш второго
        сообщения.
    """
    sk = ecdsa.SigningKey.generate(curve=ecdsa.NIST224p)

    vk = sk.get_verifying_key()

    signature = sk.sign(msg1.encode('utf-8'), k=42)
    signature2 = sk.sign(msg2.encode("utf-8"), k=42)

    msg_hash1 = hashlib.sha1(msg1.encode('utf-8')).digest()
    msg_hash2 = hashlib.sha1(msg2.encode('utf-8')).digest()

    return vk.pubkey.order, signature, signature2, msg_hash1, msg_hash2


def generator() -> dict[str, bytes]:
    """
    Создать уязвимые данные для атаки ECDSA с повторно используемым числом.

    Returns:
        Kwargs для запроса ReusedNonceAttackRequest.
    """
    vuln_data = generate_vulnerable_data("msg1", "msg2")

    ecdsa_args = {
        "pubkey_order": number.long_to_bytes(int(vuln_data[0])),
        "signature1": vuln_data[1],
        "signature2": vuln_data[2],
        "msg_hash1": vuln_data[3],
        "msg_hash2": vuln_data[4]
    }

    return ecdsa_args


def handler(
        message_kwargs: dict,
        channel: grpc.Channel
) -> message_definitions_pb2.ReusedNonceAttackResponse:
    """
    Вызывает удаленный сервис атаки через указанный канал.

    Args:
        message_kwargs: kwargs для запроса ReusedNonceAttackRequest.
        channel: транспортный канал для использования.
    """

    digital_signature_stub = \
            attack_service_pb2_grpc.DigitalSignatureAttackStub(channel)
    req = message_definitions_pb2.ReusedNonceAttackRequest(**message_kwargs)
    resp = digital_signature_stub.ecdsaReusedNonceAttack(req)
    return resp
