"""Модуль клиента.

Обеспечивает удобный интерфейс для создания сообщений, а также запросов к
серверам бэкэнда для получения информации об атаках.
"""

from google.protobuf import message
import grpc
import logging
import os

import client_pb2_grpc
import message_definitions_pb2

import user_input_resolver
import ecdsa_reused_nonce_handlers

BACKEND_ADDR = os.environ["BACKEND_ADDR"]
_LOGGER = logging.getLogger(__name__)

attack_handlers = {
    "ECDSA Reused Nonce attack": ecdsa_reused_nonce_handlers.handler
}

auto_generators = {
    "ECDSA Reused Nonce attack": ecdsa_reused_nonce_handlers.generator
}

prompters = {
    "ECDSA Reused Nonce attack":
        lambda: user_input_resolver.prompt_for_message(
            message_definitions_pb2.ReusedNonceAttackRequest().DESCRIPTOR)
}


def perform_attack(
        service: message_definitions_pb2.AvailableServices.AvailableService
) -> message.Message:
    """
    Выполнить атаку с клиентской стороны.

    Запросить данные для атаки у пользователя, а затем запросить сервер
    для выполнения атаки и получения результата.

    Args:
        service: сервис, на который выполняется атака.

    Returns:
        Ответ от сервера.
    """
    with grpc.insecure_channel(service.address) as channel:

        choice = 0
        while choice not in [1, 2]:
            choice = int(input("\nPlease choose the type of the attack "
                  "you want to perform. \n\t1 - for automatic generation "
                  "of vulnerable data,  \n\t2 - for manual data "
                  "entry\n\n"))

        handler = attack_handlers[service.attack_name]
        generator = auto_generators[service.attack_name]
        prompter = prompters[service.attack_name]

        args = {}
        if choice == 1 and generator is not None:
            args = generator()

        elif choice == 1 and handler is None:
            print("There is no automatic data generation for this type of "
                  "the attack")
            choice = 2

        if choice == 2:
            print("Now you are required to enter the data to the "
                  "corresponding fields. Please ensure the correctness of "
                  "the  entered data.")
            args = prompter()
        try:
            response = handler(args, channel)
            _LOGGER.info(f"Successfull rpc call: {response}")
        except grpc.RpcError as rpc_error:
            _LOGGER.error(f"Rpc call error: {rpc_error}")
            raise RuntimeError(f"Unexpected error: {rpc_error}")
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
    with grpc.insecure_channel(backend_address) as channel:
        available_services = None
        try:
            crypto_attacks_stub = client_pb2_grpc.CryptoAttacksStub(channel)
            crypto_attack_args = message_definitions_pb2.EmptyMessage()
            available_services = crypto_attacks_stub \
                    .getAvailableServices(crypto_attack_args).services
        except Exception:
            _no_services_available()

        assert available_services is not None

        if len(available_services) == 0:
            _no_services_available()

        for idx, service in enumerate(available_services):
            print(f"======== Attack {idx} ========")
            print(service)

        try:
            chosen_attack = int(input("Choose the attack: "))
            if not (0 <= chosen_attack <= len(available_services) - 1):
                raise ValueError("Enter the correct integer value for the "
                        "attack")
            print(f"You chose: {chosen_attack}")
            attack_service = available_services[chosen_attack]
            res = perform_attack(attack_service)

            print(res)

        except ValueError as e:
            _LOGGER.error(e)


def main():
    while True:
        try:
            print("Running an interactive client, press ctrl+c to exit.")
            run(BACKEND_ADDR)
        except KeyboardInterrupt:
            print("\nExititng...")
            exit(0)
        except RuntimeError as e:
            _LOGGER.error(e)


if __name__ == "__main__":
    logging.basicConfig()
    main()
