#!/bin/env python

from os import pread
from typing import Optional, reveal_type
from Crypto.Random import get_random_bytes
from argparse import ArgumentParser
from sys import argv
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR

#TODO: connect to TCP socket
#TODO: get iv, ct
#TODO: attack
#TODO: invalid padding/message !

CLIENT_BUFFER = 1024
BLOCK_SIZE = 16


def process_block(iv: bytes, block: bytes, sock: socket, padding_error_msg: str, invalid_msg_error: str):
    cur_block = bytearray(block)
    for idx in range(BLOCK_SIZE - 1, -1, -1):
        for byte in range(256):
            cur_block[idx] = byte
            print((iv + bytes(cur_block)).hex())
            sock.send(iv + bytes(cur_block))
            print(sock.recv(CLIENT_BUFFER))

# TODO: accept function as a parameter, potentially rewrite this as a decorator
# function
def attack(vuln_addres: str, padding_error_msg: str, invalid_msg_error: str):
    with socket(AF_INET, SOCK_STREAM) as s:
        ip, port = vuln_addres.split(':')
        s.connect((ip, int(port)))

        data = s.recv(CLIENT_BUFFER)
        iv = data[:16]
        ct = data[16:]
        print(iv.hex(), ct.hex())
        num_blocks = len(ct) // BLOCK_SIZE

        process_block(iv, ct[:16], s, padding_error_msg, invalid_msg_error)

attack("127.0.0.1:31337", "invalid_padding", "invalid_message")
