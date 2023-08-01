import json

from pika import BlockingConnection, ConnectionParameters, PlainCredentials, BasicProperties
from pika.adapters.blocking_connection import BlockingChannel
from pika.exchange_type import ExchangeType

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
    ch.basic_ack(delivery_tag=method.delivery_tag)

def on_request(ch, method, props, body):
    print(f"[.] Received request for the attack data format")

    attack_data = {
        "pubkey_order": "int",
        "sig1": "(int, int)",
        "sig2": "(int, int)",
        "msg_hash1": "bytes",
        "msg_hash2": "bytes"
    }

    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=BasicProperties(correlation_id = \
                                                         props.correlation_id),
                     body=json.dumps(attack_data))
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

    # Declare a queue for receiving rpc requests for data
    rpc_queue_result = channel.queue_declare(queue="rpc_queue")
    rpc_queue = rpc_queue_result.method.queue

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=rpc_queue, on_message_callback=on_request)

    # Start consuming the queues
    channel.start_consuming()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\nInterrupted')
        exit(0)
