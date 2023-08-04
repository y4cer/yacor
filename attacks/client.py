import client_api_pb2_grpc
import message_definitions_pb2

from grpc import insecure_channel

from ecdsa_reused_nonce import (ecdsa_reused_nonce_generator,
                                        ecdsa_reused_nonce_handler)

from user_input_resolver import prompt_for_message

attack_handlers = {
    "ECDSA Reused Nonce attack": ecdsa_reused_nonce_handler
}

auto_generators = {
    "ECDSA Reused Nonce attack": ecdsa_reused_nonce_generator
}

prompters = {
    "ECDSA Reused Nonce attack":
        lambda: prompt_for_message(message_definitions_pb2 \
                                   .ReusedNonceAttackRequest().DESCRIPTOR)
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

def run(backend_address):
    with insecure_channel(backend_address) as channel:
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

while True:
    run('localhost:50051')
