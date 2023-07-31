#!/bin/env python

from os import pread
from typing import Optional, reveal_type
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from argparse import ArgumentParser
from sys import argv
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR

data = b'secret data'

CLIENT_BUFFER = 1024
BLOCK_SIZE = 16

class Server:

    key: Optional[bytes]
    sock: socket


    def __init__(self, port: int):
        # TODO: add port and key constraint checking
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.sock.bind(("0.0.0.0", port))
        self.sock.listen()


    def _pad(self, message):
        """Pad the message with the PKCS7 padding"""
        bytes_to_pad = AES.block_size - (len(message) % AES.block_size)
        print(bytes_to_pad)
        return message + \
                int.to_bytes(bytes_to_pad, byteorder="little") * bytes_to_pad


    def _unpad(self, message):
        """Try to unpad the message with the PKCS7 padding
        Raises:
            ValueError if the message padding is incorrect"""
        padding_byte = message[-1]
        if padding_byte < 1 or padding_byte > 16 or \
                padding_byte >= len(message):
            raise ValueError("Incorrect padding!")

        for i in range(1, padding_byte + 1):
            if message[-i] != padding_byte:
                raise ValueError("Incorrect padding!")

        return message[:-padding_byte]

    def _check_ct(self, ct, message):
        try:
            pt_ = self.cipher.decrypt(ct)
            pt = self._unpad(pt_)

        # TODO: logging
        except ValueError:
            return 0

        if pt != message:
            return 1
        else:
            return 2


    # TODO: spawn this in a separate thread and then add gracefully_stop
    # function
    def serve_forever(self, message: bytes, key: bytes, iv: bytes):
        self.key = key
        print(len(key))
        print(message)
        self.cipher = AES.new(key, AES.MODE_CBC, iv=iv)
        while True:
            conn, _ = self.sock.accept()
            padded = self._pad(message)
            server_ct = self.cipher.encrypt(padded)
            conn.sendall(bytes(self.cipher.iv) + server_ct)
            print(f"{self.cipher.iv.hex()=}, {server_ct.hex()=}")
            received_ct = self.sock.recv(CLIENT_BUFFER)
            print(received_ct.hex())
            status = self._check_ct(received_ct, message)

            # TODO: status codes
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
    default_key = "0"*32
    parser.add_argument("-p", "--port", dest="port", type=int, default=31337,
                        help="port to accept connections, default is 31337")
    parser.add_argument("-k", "--key", dest="key", help="key"  \
                        " to initialize the AES cipher", default=default_key)
    parser.add_argument("-m", "--message", dest="message", help="message to \
                        encrypt", default=default_key * 2 + "asd")
    parser.add_argument("--iv", dest="iv", help="initialization vector for the \
                        algorithm", default=default_key)

    args = parser.parse_args()

    # TODO: check for None
    key = bytes.fromhex(args.key)
    message = args.message.encode()
    iv = bytes.fromhex(args.iv)

    # print(key, message, iv)
    # print(len(key))
    serv = Server(args.port)
    serv.serve_forever(message, key, iv)
