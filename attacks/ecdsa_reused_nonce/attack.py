import hashlib
import base64
from typing import reveal_type

from ecdsa.ecdsa import Signature
from ecdsa.numbertheory import inverse_mod
from ecdsa import SigningKey, VerifyingKey, der
from Crypto.Util.number import long_to_bytes, bytes_to_long

from ecdsa import SigningKey, NIST224p
from ecdsa.util import sigencode_string, sigdecode_string
from ecdsa.numbertheory import inverse_mod
from hashlib import sha1

def attack(*, pubkey_order, sig1, sig2, msg_hash1, msg_hash2):
    r1, s1 = sigdecode_string(sig1, pubkey_order)
    r2, s2 = sigdecode_string(sig2, pubkey_order)
    #Convert Hex into Int
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

    # print(f"Actual private key: \t {long_to_bytes(int(sk.privkey.secret_multiplier))}")

    vk = sk.get_verifying_key()

    signature = sk.sign(msg1.encode('utf-8'), k=22)

    # r1, s1 = sigdecode_string(signature, vk.pubkey.order)

    signature2 = sk.sign(msg2.encode("utf-8"), k=22)

    # r2, s2 = sigdecode_string(signature2, vk.pubkey.order)

    msg_hash1 = sha1(msg1.encode('utf-8')).digest()
    msg_hash2 = sha1(msg2.encode('utf-8')).digest()

    return vk.pubkey.order, signature, signature2, msg_hash1, msg_hash2

if __name__ == "__main__":

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
