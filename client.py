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

primitive_type_enum = {
    0: "PRIMITIVE_TYPE_UNSPECIFIED",
    1: "PRIMITIVE_TYPE_HASH",
    2: "PRIMITIVE_TYPE_DIGITAL_SIGNATURE",
    3: "PRIMITIVE_TYPE_SYMMETRIC"
}


def ecdsa_reused_nonce_handler():
    digital_signature_stub = client_api_pb2_grpc.DigitalSignatureAttackServiceStub(channel)
    req = message_definitions_pb2.ReusedNonceAttackRequest()

    test = message_definitions_pb2.TestMessage()

    kwargs = prompt_for_message(test.DESCRIPTOR)
    message_definitions_pb2.TestMessage(**kwargs)

    req_args = {}
    for field in req.DESCRIPTOR.fields:
        req_args[field.name] = prompt_for_data(field)
        print(field.name, field.type)

    vuln_data = generate_vulnerable_data("msg1", "msg2")

    pubkey_order = long_to_bytes(int(vuln_data[0]))

    ecdsa_args = {"pubkey_order": pubkey_order,
                  "signature1": vuln_data[1],
                  "signature2": vuln_data[2],
                  "msg_hash1": vuln_data[3],
                  "msg_hash2": vuln_data[4]
    }
    return ecdsa_args


attack_handlers = {
    "ECDSA Reused Nonce attack": ecdsa_reused_nonce_handler
}


def perform_attack(service: message_definitions_pb2.AvailableServices.AvailableService):
    with insecure_channel(service.address) as channel:
        reflection_db = ProtoReflectionDescriptorDatabase(channel)

        desc_pool = DescriptorPool(reflection_db)
        service_desc = desc_pool.FindServiceByName(f"{service.package_name}.{service.service_name}")
        service_stub = None
        service_stub = eval(f"{service.proto_name}_pb2_grpc.{service.service_name}Stub(channel)")
        assert service_stub is not None

        print(f"\tclient: found {service.service_name} service with name: {service_desc.full_name}")

        for method in service_desc.methods:
            print(f"\tclient: found method name: {method.full_name}")
            input_type = method.input_type
            output_type = method.output_type
            print(f"\tclient: found input type for this method: {input_type.full_name}")

            request_desc = desc_pool.FindMessageTypeByName(
                input_type.full_name
            )
            response_desc = desc_pool.FindMessageTypeByName(
                output_type.full_name
            )

            print(f"\tclient: found request name: {request_desc.full_name}")

            choice = 0
            while choice not in [1, 2]:
                choice = int(input("\nPlease choose the type of the attack " \
                      "you want to perform. \n\t1 - for automatic generation " \
                      "of vulnerable data,  \n\t2 - for manual data " \
                      "entry\n\n"))

            handler = attack_handlers[service.attack_name]

            args = {}
            if choice == 1 and handler is not None:
                args = handler()

            elif choice == 1 and handler is None:
                print("There is no automatic data generation for this type of the attack")
                choice = 2

            if choice == 2:
                print("Now you are required to enter the data to the corresponding fields. Please ensure the correctness of the entered data.")
                for field in request_desc.fields:
                    res = None
                    while res is None:
                        res = prompt_for_data(field)
                    args[field.name] = res

            msg = eval(f"message_definitions_pb2.{input_type.name}(**args)")

            # !!!!!!!!! VERY IMPORTANT !!!!!!!!!!!!!!!
            # for field in msg.ListFields():
            #     print(field[0].name, field[0].type)
            # !!!!!!!!! VERY IMPORTANT !!!!!!!!!!!!!!!

            resp = eval(f"service_stub.{method.name}(msg)")
            for field in response_desc.fields:
                print(field.name, eval(f"resp.{field.name}"))
            print(args)

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
