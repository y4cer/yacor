"""Модуль клиента.

Обеспечивает удобный интерфейс для создания сообщений, а также запросов к
серверам бэкэнда для получения информации об атаках.
"""

from google.protobuf.message import Message
from grpc import insecure_channel

import client_pb2_grpc
from message_definitions_pb2 import (ReusedNonceAttackRequest,
                                     AvailableServices,
                                     EmptyMessage)

from user_input_resolver import prompt_for_message
from ecdsa_reused_nonce import (ecdsa_reused_nonce_generator,
                                ecdsa_reused_nonce_handler)

attack_handlers = {
    "ECDSA Reused Nonce attack": ecdsa_reused_nonce_handler
}

auto_generators = {
    "ECDSA Reused Nonce attack": ecdsa_reused_nonce_generator
}

prompters = {
    "ECDSA Reused Nonce attack":
        lambda: prompt_for_message(ReusedNonceAttackRequest().DESCRIPTOR)
}

def perform_attack(service: AvailableServices.AvailableService) -> Message:
    """
    Выполнить атаку с клиентской стороны.

    Запросить данные для атаки у пользователя, а затем запросить сервер
    для выполнения атаки и получения результата.

    Args:
        service: сервис, на который выполняется атака.

    Returns:
        Ответ от сервера.
    """
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
            print("There is no automatic data generation for this type of " \
                    "the attack")
            choice = 2

        if choice == 2:
            print("Now you are required to enter the data to the " \
                  "corresponding fields. Please ensure the correctness of " \
                  "the  entered data.")
            args = prompter()

        response = handler(args, channel)
        return response

def _no_services_available() -> None:
    print("Sorry, there are currently no available attack services")
    exit(0)

def run(backend_address: str) -> None:
    """
    Запустить клиентский запрос.

    Args:
        backend_address: адрес сервера бэкэнда, на который отправляется
        начальный запрос.
    """
    with insecure_channel(backend_address) as channel:
        available_services = None
        try:
            crypto_attacks_stub = client_pb2_grpc.CryptoAttacksStub(channel)
            crypto_attack_args = EmptyMessage()
            available_services = crypto_attacks_stub \
                    .getAvailableServices(crypto_attack_args).services
        except Exception as e:
            print(e)
            _no_services_available()

        assert available_services is not None

        if len(available_services) == 0:
            _no_services_available()

        for idx, service in enumerate(available_services):
            print(f"======== Attack {idx} ========")
            print(service)
            print(f"primitive_type is: {service.primitive_type}")
            print(f"attack name is: {service.attack_name}")

        try:
            chosen_attack = int(input("Choose the attack: "))
            if not (0 <= chosen_attack <= len(available_services) - 1):
                raise ValueError("Enter the correct integer value for the " \
                        "attack")
            print(f"You chose: {chosen_attack}")
            attack_service = available_services[chosen_attack]
            res = perform_attack(attack_service)
            print(res)

        except ValueError as e:
            print(e)


while True:
    try:
        print("Running an interactive client, press ctrl+c to exit.")
        run('localhost:50051')
    except KeyboardInterrupt:
        print("\nExititng...")
        exit(0)
