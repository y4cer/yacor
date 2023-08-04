# yacor

## Description
This is the demo-version of the cryptanalytic tool. yacor is a service for
security analysis of the blockchain cryptographic primitives.

## Disclaimer
I strongly encourage using this project only in scientific or research
purposes.

## Reference architecture
```
                                            ┌───────────────────────────────┐
                                            │                               │
                                    ┌──────►│  ECDSA reused nonce attack    │
┌─────────┐                         │       │                               │
│         │                         │       └───────────────────────────────┘
│ Client  │◄──┬─ ── ── ── ── ── ── ─┤
│         │   │                     ├───┐   ┌───────────────────────────────┐
└─────────┘   │   ┌─────────────┐   │   │   │                               │
              │   │             │   │   └──►│  Other attack(s)              │
              └──►│   Backend   │◄──┘       │                               │
                  │             │           └───────────────────────────────┘
                  └─────────────┘
```
The yacor project consists of 3 main modules:
1. **Client**: simple python client which firstly retrieves information about
available services and then makes attack requests to these services.
2. **Backend**: gRPC python backend, which exposes 2 APIs: one for client
information retrieval, the second one is for attack services to "subscribe"
to the backend and make them visible to the client. Once attack service is
subscribed, backend starts doing periodical healthchecks to have the most
recent information present for the client. Backend also acts as a load-balancer
between client and multiple attack services implementing the same attack.
3. **Attack service(s)**: gRPC python service, which exposes 2 services: one
for healthchecks, other one is for the processing of the user requests. Once
the service is started, it immediately informs the backend of its serving status
and starts to respond to healthcheck messages.

## Technology stack
Python, python-gRPC, google-protobuf

## Deployment

## Installation
1. Install python, docker-compose and Docker according to your system guides.
Then, execute:
```sh
python -m venv env
source env/bin/activate
pip3 install --upgrade -r requirements.txt
```
To install all needed requirements into the newly created Python virtual
environment.

2. Then run make to generate all protobuf declarations.
```sh
make all
```

To clean generated proto definitions, run `make clean`.
## Usage

### Run the project locally via docker-compose
The best way to run this project without any headaches is to use docker-compose.
```sh
docker-compose up
```
Then you will see the periodical healthcheck logs made by backend service.

Then run
```sh
python client.py
```
To connect to the remote backend service to retrieve all information about
running services and choose the attack.

## License
Licensed under BSD 3-Clause License. y4cer @ 2023.
