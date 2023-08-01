import json
from pika import BlockingConnection, ConnectionParameters, PlainCredentials, BasicProperties
from pika.adapters.blocking_connection import BlockingChannel
from pika.exchange_type import ExchangeType
from Crypto.Util.number import bytes_to_long

from attack import attack

RMQ_HOST = 'localhost'
RMQ_PORT = 5672
RMQ_USER = 'rabbit'
RMQ_PASS = '1234'

#TODO: change this
EXCHANGE_NAME = 'amq.topic'
#TODO: add enums
ROUTING_KEY = 'digital_signatures.ecdsa_nonce_reuse'

credentials = PlainCredentials(RMQ_USER, RMQ_PASS)
parameters = ConnectionParameters(RMQ_HOST,
                                  RMQ_PORT,
                                  credentials=credentials)


# TODO: typings
def attack_primitive(ch, method, properties, body):
    data = json.loads(body)
    print(f" [x] Received {data}")
    data = {
        "pubkey_order": bytes_to_long(bytes.fromhex(data["pubkey_order"])),
        "sig1": bytes.fromhex(data["sig1"]),
        "sig2": bytes.fromhex(data["sig2"]),
        "msg_hash1": bytes.fromhex(data["msg_hash1"]),
        "msg_hash2": bytes.fromhex(data["msg_hash2"])
    }

    print(f"Recovered private key: {attack(**data)}")

    ch.basic_ack(delivery_tag=method.delivery_tag)


def main():
    connection = BlockingConnection(parameters)
    channel = connection.channel()

    # Declare a queue for receiving messages to atttack
    tmp_queue_ = channel.queue_declare('', exclusive=True)
    tmp_queue_name = tmp_queue_.method.queue

    channel.queue_bind(exchange=EXCHANGE_NAME,
                       queue=tmp_queue_name, routing_key=ROUTING_KEY)
    channel.basic_consume(queue=tmp_queue_name, on_message_callback=attack_primitive)

    # Start consuming the queue
    channel.start_consuming()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\nInterrupted')
        exit(0)
