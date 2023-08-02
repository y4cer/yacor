# yacor

## Description
This is the demo-version of the cryptanalytic tool. Yacor is a service for
security analysis of the blockchain cryptographic primitives.

## Reference architecture
```
                                                    ┌───────────────────────────────┐
                                                    │                               │
                                                ┌───┤  ECDSA reused nonce attack    │
┌─────────┐               ┌─────────────┐       │   │                               │
│         │               │             │       │   └───────────────────────────────┘
│ Client  │◄─────────────►│   Backend   ├───────┤
│         │               │             │       │   ┌───────────────────────────────┐
└─────────┘               └─────────────┘       │   │                               │
                                                └───┤  Other attack(s)              │
                                                    │                               │
                                                    └───────────────────────────────┘
```
## Technology stack
Python, python-gRPC, google-protobuf

## Deployment

## Installation

## Usage
Firstly, (re-)generate needed protobuf definitions:
```sh
make
```

To clear generated definitions, run:
```sh
make clean
```

Then, run backend, interact\_module and client in 3 separate terminal emulators:
```sh
python backend.py
```

```sh
python attacks/interact_module.py
```

```sh
python client.py
```

When you run the `interact_module.py`, you will see that it has been
successfully registered at backend. Backend performs regular healthchecks.


## License
Licensed under BSD 3-Clause License. y4cer @ 2023.
