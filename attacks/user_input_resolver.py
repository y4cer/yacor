"""Helper module containing functions for parsing protobuf Messages."""

from __future__ import annotations
from google.protobuf import message_factory
from google.protobuf.descriptor import Descriptor, FieldDescriptor

# Google protobuf field types from the official documentation v 4.21.1
# https://googleapis.dev/python/protobuf/latest/google/protobuf/descriptor.html#google.protobuf.descriptor.FieldDescriptor
_field_types = {
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

_field_labels = {
    1: "LABEL_OPTIONAL",
    2: "LABEL_REQUIRED",
    3: "LABEL_REPEATED"
}

_grpc_integer_types = ["TYPE_FIXED32", "TYPE_FIXED64",
                      "TYPE_INT32", "TYPE_INT64",
                      "TYPE_SFIXED32", "TYPE_SFIXED64",
                      "TYPE_SINT32", "TYPE_SINT64",
                      "TYPE_UINT32", "TYPE_UINT64"
                      ]


def _get_data_with_prompt(field_name: str, prompt: str) -> str:
    data = input(f"{field_name} ({prompt}): ")
    return data


def _prompt_for_data(
        field: FieldDescriptor
) -> bytes | bool | float | int | str | None:
    try:
        match _field_types[field.type]:

            case "TYPE_BYTES":
                data = _get_data_with_prompt(field.name, "hex encoded bytestring")
                return bytes.fromhex(data)

            case "TYPE_BOOL":
                data = _get_data_with_prompt(field.name, "true/false")
                if data == "true":
                    return True
                elif data == "false":
                    return False
                else:
                    raise ValueError("Only true/false is allowed!")

            case "TYPE_DOUBLE" | "TYPE_FLOAT":
                data = _get_data_with_prompt(field.name, "float or double value")
                return float(data)

            case w if w in _grpc_integer_types:
                data = _get_data_with_prompt(field.name, "integer value")
                return int(data)

            case "TYPE_STRING":
                data = _get_data_with_prompt(field.name, "string value")
                return data

            case _:
                return 0

    except ValueError as e:
        print(e)
        return None


def _prompt_for_enum_data(prompting_dict: dict[int, str]) -> int:
    print("Available enum types: ")
    for k, v in prompting_dict.items():
        print(f"{k}: {v}")
    n = None
    while n is None:
        try:
            n = int(input("Please enter the integer value for the enum: "))
            if n not in prompting_dict.keys():
                n = None
                raise ValueError("Enter a valid key!")
        except ValueError as e:
            print(e)
    return n


def prompt_for_message(message_desc: Descriptor) -> dict:
    """
    Prompt user for entering valid values for the protobuf Message.

    Args:
        message_desc: Descriptor for the message class to enter.

    Returns:
        dictionary of values to create the message from.
    """
    print(f"Prompting data for {message_desc.name}")
    res_kwargs = {}
    for field in message_desc.fields:
        n = 1
        entries = []

        if _field_labels[field.label] == "LABEL_REPEATED":
            n = int(input("Please type the number of entries you want to insert: "))

        for i in range(n):
            #TODO: press ctrl+c to stop entering data
            if n > 1:
                print(f"Prompting for entry #{i + 1}")

            data = None
            if nested_msg_desc := field.message_type:
                kwargs = prompt_for_message(field.message_type)
                nested_msg = message_factory.MessageFactory() \
                                        .GetPrototype(nested_msg_desc)
                entries.append(nested_msg(**kwargs))
            elif enum_desc := field.enum_type:
                enum_dict = enum_desc.values_by_name
                prompting_dict = {}
                for idx, k in enumerate(enum_dict):
                    prompting_dict[idx] = k
                idx = _prompt_for_enum_data(prompting_dict)
                entries.append(idx)
            else:
                while data is None:
                    data = _prompt_for_data(field)
                entries.append(data)

        if n > 1 or _field_labels[field.label] == "LABEL_REPEATED":
            res_kwargs[field.name] = entries
        else:
            res_kwargs[field.name] = entries[0]
    return res_kwargs
