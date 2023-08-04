from typing import Iterable, reveal_type

from google.protobuf.descriptor import Descriptor, FieldDescriptor, FileDescriptor
import client_api_pb2_grpc
import client_api_pb2
import message_definitions_pb2
import attack_service_api_pb2
import attack_service_api_pb2_grpc

from grpc import insecure_channel
from Crypto.Util.number import long_to_bytes
from google.protobuf.descriptor_pool import DescriptorPool
from grpc_reflection.v1alpha.proto_reflection_descriptor_database import (
    ProtoReflectionDescriptorDatabase,
)

from attacks.ecdsa_reused_nonce.attack import generate_vulnerable_data
from client_tools.user_input_resolver import prompt_for_data, prompt_for_message


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


def ecdsa_reused_nonce_handler(message_kwargs, channel):
    digital_signature_stub = attack_service_api_pb2_grpc.DigitalSignatureAttackServiceStub(channel)
    req = message_definitions_pb2.ReusedNonceAttackRequest(**message_kwargs)
    resp = digital_signature_stub.ecdsaReusedNonceAttack(req)
    return resp

attack_handlers = {
    "ECDSA Reused Nonce attack": ecdsa_reused_nonce_handler
}

auto_generators = {
    "ECDSA Reused Nonce attack": ecdsa_reused_nonce_generator
}

prompters = {
    "ECDSA Reused Nonce attack": lambda: prompt_for_message(message_definitions_pb2.ReusedNonceAttackRequest().DESCRIPTOR)
}

def perform_attack(service: message_definitions_pb2.AvailableServices.AvailableService):
    with insecure_channel(service.address) as channel:

        choice = 0
        while choice not in [1, 2]:
            choice = int(input("\nPlease choose the type of the attack " \
                  "you want to perform. \n\t1 - for automatic generation " \
                  "of vulnerable data,  \n\t2 - for manual data " \
                  "entry\n\n"))

        handler = attack_handlers[service.attack_name]
        generator = auto_generators[service.attack_name]
        prompter = prompters[service.attack_name]

        args = {}
        if choice == 1 and generator is not None:
            args = generator()

        elif choice == 1 and handler is None:
            print("There is no automatic data generation for this type of the attack")
            choice = 2

        if choice == 2:
            print("Now you are required to enter the data to the corresponding fields. Please ensure the correctness of the entered data.")
            args = prompter()

        response = handler(args, channel)
        print(response)

def no_services_available():
    print("Sorry, there are currently no available attack services")
    exit(0)

with insecure_channel('localhost:50051') as channel:
    available_services = None

    try:
        crypto_attacks_stub = client_api_pb2_grpc.CryptoAttacksServiceStub(channel)
        crypto_attack_args = message_definitions_pb2.EmptyMessage()
        available_services = crypto_attacks_stub.getAvailableServices(crypto_attack_args).services
    except Exception as e:
        print(e)
        no_services_available()

    assert available_services is not None

    if len(available_services) == 0:
        no_services_available()

    for idx, service in enumerate(available_services):
        print(f"======== Attack {idx} ========")
        print(service)
        print(f"primitive_type is: {service.primitive_type}")
        print(f"attack name is: {service.attack_name}")

    chosen_attack = int(input("Choose the attack: "))
    #TODO: check for 0 and not ints
    assert 0 <= chosen_attack <= len(available_services) - 1

    print(f"You chose: {chosen_attack}")
    attack_service = available_services[chosen_attack]

    perform_attack(attack_service)
