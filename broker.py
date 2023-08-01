import json
from datetime import datetime

from pika import BlockingConnection, ConnectionParameters, PlainCredentials, BasicProperties
from pika.exchange_type import ExchangeType
import uuid

RMQ_HOST = 'localhost'
RMQ_PORT = 5672
RMQ_USER = 'rabbit'
RMQ_PASS = '1234'
#TODO: change this
EXCHANGE_NAME = 'amq.topic'
ROUTING_KEY = 'digital_signatures.ecdsa_nonce_reuse'

class MessageBroker(object):

    def __init__(self):
        credentials = PlainCredentials(RMQ_USER, RMQ_PASS)
        parameters = ConnectionParameters(RMQ_HOST,
                                          RMQ_PORT,
                                          credentials=credentials)
        self.connection = BlockingConnection(parameters)

        self.channel = self.connection.channel()

        rpc_queue_result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = rpc_queue_result.method.queue

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True)

        self.response = None
        self.corr_id = None

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def get_attack_data_format(self):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange='',
            routing_key='rpc_queue',
            properties=BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
            ),
            body="")
        self.connection.process_data_events(time_limit=5)
        return self.response

    def act(self, n):
        data = {
            "pubkey_order": n,
            "sig1": "(int, int)",
            "sig2": "(int, int)",
            "msg_hash1": "bytes",
            "msg_hash2": "bytes"
        }

        self.channel.basic_publish(exchange=EXCHANGE_NAME,
                  routing_key=ROUTING_KEY,
                  body=json.dumps(data).encode())


broker = MessageBroker()

if __name__ == '__main__':
    while True:
        try:
            n = int(input("enter the number: "))
            if n == 1:
                print(broker.get_attack_data_format())
            else:
                print(broker.act(n))
        except KeyboardInterrupt:
            print('\nInterrupted')
            exit(0)
