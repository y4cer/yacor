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
# EXCHANGE_NAME = 'cryptographic_attacks'
#TODO: add enums
ROUTING_KEY = 'digital_signatures.ecdsa_nonce_reuse'

credentials = PlainCredentials(RMQ_USER, RMQ_PASS)
parameters = ConnectionParameters(RMQ_HOST,
                                  RMQ_PORT,
                                  credentials=credentials)


def callback(ch, method, properties, body):
    data = json.loads(body)
    print(f" [x] Received {data}")
    # if data['value'] > 500:
    #     print(f"{data['time']}: WARNING")
    # else:
    #     print(f"{data['time']}: OK")

    # with open('receiver.log', 'a') as f:
    #     json.dump(data, f)
    #     f.write('\n')

    ch.basic_ack(delivery_tag=method.delivery_tag)

def fib(n):
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fib(n - 1) + fib(n - 2)

def on_request(ch, method, props, body):
    n = int(body)

    print(f" [.] fib({n})")
    response = fib(n)

    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=BasicProperties(correlation_id = \
                                                         props.correlation_id),
                     body=str(response))
    ch.basic_ack(delivery_tag=method.delivery_tag)


def main(ROUTING_KEY):
    connection = BlockingConnection(parameters)
    channel = connection.channel()

    result = channel.queue_declare('', exclusive=True)
    queue_name = result.method.queue

    rpc_queue_result = channel.queue_declare(queue="rpc_queue")
    rpc_queue = rpc_queue_result.method.queue

    channel.queue_bind(exchange=EXCHANGE_NAME,
                       queue=queue_name, routing_key=ROUTING_KEY)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=rpc_queue, on_message_callback=on_request)
    channel.basic_consume(queue=queue_name, on_message_callback=callback)

    channel.start_consuming()


if __name__ == '__main__':
    try:
        main(ROUTING_KEY)
    except KeyboardInterrupt:
        print('\nInterrupted')
        exit(0)
