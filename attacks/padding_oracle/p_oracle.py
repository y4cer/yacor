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

attack("127.0.0.1:31337", "invalid_padding", "invalid_message")
