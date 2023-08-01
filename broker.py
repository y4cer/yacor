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


    def act(self, ROUTING_KEY, data):
        # data = {
        #     "pubkey_order": "123",
        #     "sig1": "(int, int)",
        #     "sig2": "(int, int)",
        #     "msg_hash1": "bytes",
        #     "msg_hash2": "bytes"
        # }

        ##TODO: change this!!!
        #data = {}
        #for i in range(len(args)):
        #    data[i] = args[i].hex()

        self.channel.basic_publish(exchange=EXCHANGE_NAME,
                  routing_key=ROUTING_KEY,
                  body=json.dumps(data).encode())


broker = MessageBroker()

if __name__ == '__main__':
    while True:
        try:
            n = int(input("enter the number: "))
            print(broker.act(n, {"":""}))
        except KeyboardInterrupt:
            print('\nInterrupted')
            exit(0)
