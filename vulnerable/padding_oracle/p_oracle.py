#!/bin/env python

from typing import Optional, reveal_type
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from argparse import ArgumentParser
from sys import argv
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR

data = b'secret data'

CLIENT_BUFFER = 1024

class Server:

    key: Optional[bytes]
    sock: socket


    def __init__(self, port: int):
        # TODO: add port and key constraint checking
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.sock.bind(("0.0.0.0", port))
        self.sock.listen()


    def pad(self):
        pass


    def unpad(self):
        pass


    def _check_ct(self, ct):
        return 1


    # TODO: spawn this in a separate thread and then add gracefully_stop
    # function
    def serve_forever(self, message: bytes, key, iv):
        self.key = key
        self.cipher = AES.new(key, AES.MODE_CBC, iv=iv)
        while True:
            conn, addr = self.sock.accept()
            server_ct = self.cipher.encrypt(message)
            conn.sendall(bytes(self.cipher.iv) + server_ct)
            received_ct = self.sock.recv(CLIENT_BUFFER)

            status = self._check_ct(received_ct)

            if status == 0:
                conn.sendall("invalid padding".encode())
            elif status == 1:
                conn.sendall("invalid message".encode())
            else:
                conn.sendall("correct!".encode())

            conn.close()


if __name__ == "__main__":
    parser = ArgumentParser(prog=argv[0],
                            description="""This python script starts the server
                            which is vulnerable to the padding oracle attack
                            for AES in the CBC mode.""")
    parser.add_argument("-k", "--key", required=True, dest="key", help="key" \
                                            " to initialize the AES cipher")
    parser.add_argument("-p", "--port", dest="port", type=int, default=31337,
                        help="port to accept connections, default is 31337")
    parser.add_argument("-m", "--message", dest="message", help="message to \
                        encrypt")
    parser.add_argument("--iv", dest="iv", help="initialization vector for the \
                        algorithm")

    args = parser.parse_args()


    serv = Server(args.port)
    serv.serve_forever(args.key, args.message, args.iv)
