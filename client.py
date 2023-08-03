from typing import Iterable, reveal_type

from google.protobuf.descriptor import FileDescriptor
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

primitive_type_enum = {
    0: "PRIMITIVE_TYPE_UNSPECIFIED",
    1: "PRIMITIVE_TYPE_HASH",
    2: "PRIMITIVE_TYPE_DIGITAL_SIGNATURE",
    3: "PRIMITIVE_TYPE_SYMMETRIC"
}

field_types = {
    8: "TYPE_BOOL",
   12: "TYPE_BYTES",
    1: "TYPE_DOUBLE",
   14: "TYPE_ENUM",
    7: "TYPE_FIXED32",
    6: "TYPE_FIXED64",
    2: "TYPE_FLOAT",
   10: "TYPE_GROUP",
    5: "TYPE_INT32",
    3: "TYPE_INT64",
   11: "TYPE_MESSAGE",
   15: "TYPE_SFIXED32",
   16: "TYPE_SFIXED64",
   17: "TYPE_SINT32",
   18: "TYPE_SINT64",
    9: "TYPE_STRING",
   13: "TYPE_UINT32",
    4: "TYPE_UINT64",
}

grpc_integer_types = ["TYPE_FIXED32", "TYPE_FIXED64",
                      "TYPE_INT32", "TYPE_INT64",
                      "TYPE_SFIXED32", "TYPE_SFIXED64",
                      "TYPE_SINT32", "TYPE_SINT64",
                      "TYPE_UINT32", "TYPE_UINT64"
                      ]

def ecdsa_reused_nonce_handler():
    vuln_data = generate_vulnerable_data("msg1", "msg2")

    pubkey_order = long_to_bytes(int(vuln_data[0]))

    ecdsa_args = {"pubkey_order": pubkey_order,
                  "signature1": vuln_data[1],
                  "signature2": vuln_data[2],
                  "msg_hash1": vuln_data[3],
                  "msg_hash2": vuln_data[4]
    }
    return ecdsa_args

def get_data_with_prompt(field_name, prompt):
    data = input(f"{field_name} ({prompt}): ")
    return data

def prompt_for_data(field: FileDescriptor):
    try:
        match field_types[field.type]:

            case "TYPE_BYTES":
                data = get_data_with_prompt(field.name, "hex encoded bytestring")
                return bytes.fromhex(data)

            case "TYPE_BOOL":
                data = get_data_with_prompt(field.name, "true/false")
                if data == "true":
                    return True
                elif data == "false":
                    return False
                else:
                    raise ValueError("Only true/false is allowed!")

            case "TYPE_DOUBLE" | "TYPE_FLOAT":
                data = get_data_with_prompt(field.name, "float or double value")
                return float(data)

            case w if w in grpc_integer_types:
                data = get_data_with_prompt(field.name, "integer value")
                return int(data)

            case "TYPE_STRING":
                data = get_data_with_prompt(field.name, "string value")
                return data

    except ValueError as e:
        print(e)
        return None

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
    #TODO: check for 0
    assert 0 <= chosen_attack <= len(available_services) - 1

    print(f"You chose: {chosen_attack}")
    attack_service = available_services[chosen_attack]

    perform_attack(attack_service)
