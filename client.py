from typing import reveal_type
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

message_types = {
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

def perform_attack(service: message_definitions_pb2.AvailableServices.AvailableService):
    with insecure_channel(service.address) as channel:
        reflection_db = ProtoReflectionDescriptorDatabase(channel)
        services = reflection_db.get_services()
        print(f"found services: {services}")
        desc_pool = DescriptorPool(reflection_db)
        service_desc = desc_pool.FindServiceByName(f"{service.package_name}.{service.service_name}")
        service_stub = None
        service_stub = eval(f"{service.proto_name}_pb2_grpc.{service.service_name}Stub(channel)")
        assert service_stub is not None

        print(f"found {service.service_name} service with name: {service_desc.full_name}")

        for methods in service_desc.methods:
            print(f"found method name: {methods.full_name}")
            input_type = methods.input_type
            print(f"input type for this method: {input_type.full_name}")
            vuln_data = generate_vulnerable_data("msg1", "msg2")

            pubkey_order = long_to_bytes(int(vuln_data[0]))

            ecdsa_args = {"pubkey_order": pubkey_order,
                          "signature1": vuln_data[1],
                          "signature2": vuln_data[2],
                          "msg_hash1": vuln_data[3].encode(),
                          "msg_hash2": vuln_data[4].encode()
                          }

            request_desc = desc_pool.FindMessageTypeByName(
                input_type.full_name
            )

            print(f"found request name: {request_desc.full_name}")
            args = {}
            for field in request_desc.fields:
                args[field.name] = ecdsa_args[field.name]
                print(field.name, message_types[field.type])

            msg = eval(f"message_definitions_pb2.{input_type.name}(**args)")
            aaa = f"service_stub.{methods.name}"
            print(aaa)
            resp = eval(f"{aaa}(msg)")
            print(resp.private_key)
            print(args)





with insecure_channel('localhost:50051') as channel:
        crypto_attacks_stub = client_api_pb2_grpc.CryptoAttacksServiceStub(channel)
        crypto_attack_args = message_definitions_pb2.EmptyMessage()

        available_services = crypto_attacks_stub.getAvailableServices(crypto_attack_args).services

        for idx, service in enumerate(available_services):
            print(f"======== {idx} ========")
            print(service)
            print(f"primitive_type is: {service.primitive_type}")
            print(f"attack name is: {service.attack_name}")

        chosen_attack = int(input("Choose the attack: "))
        #TODO: check for 0
        assert 0 <= chosen_attack <= len(available_services) - 1

        print("You have chosen: {chosen_attack}")
        attack_service = available_services[chosen_attack]

        perform_attack(attack_service)

        digital_signature_stub = client_api_pb2_grpc.DigitalSignatureAttackServiceStub(channel)
        vuln_data = generate_vulnerable_data("msg1", "msg2")

        pubkey_order = long_to_bytes(int(vuln_data[0]))

        ecdsa_args = message_definitions_pb2.ReusedNonceAttackRequest(pubkey_order=pubkey_order,
                                                       signature1=vuln_data[1],
                                                       signature2=vuln_data[2],
                                                       msg_hash1=vuln_data[3].encode(),
                                                       msg_hash2=vuln_data[4].encode())
        print(digital_signature_stub.ecdsaReusedNonceAttack(ecdsa_args))
