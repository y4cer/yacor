# Regenerates all generated files in the Python examples directory.
ARTIFACTS=

BACKEND=

BACKEND += ./backend/attack_service_pb2.py
BACKEND += ./backend/attack_service_pb2_grpc.py
BACKEND += ./backend/attack_service_pb2.pyi

BACKEND += ./backend/client_pb2.py
BACKEND += ./backend/client_pb2_grpc.py
BACKEND += ./backend/client_pb2.pyi

BACKEND += ./backend/backend_pb2.py
BACKEND += ./backend/backend_pb2_grpc.py
BACKEND += ./backend/backend_pb2.pyi

BACKEND += ./backend/message_definitions_pb2.py
BACKEND += ./backend/message_definitions_pb2_grpc.py
BACKEND += ./backend/message_definitions_pb2.pyi

ARTIFACTS += ${BACKEND}

CLIENT=

CLIENT += ./client/client_pb2.py
CLIENT += ./client/client_pb2_grpc.py
CLIENT += ./client/client_pb2.pyi

CLIENT += ./client/attack_service_pb2.py
CLIENT += ./client/attack_service_pb2_grpc.py
CLIENT += ./client/attack_service_pb2.pyi

CLIENT += ./client/backend_pb2.py
CLIENT += ./client/backend_pb2_grpc.py
CLIENT += ./client/backend_pb2.pyi

CLIENT += ./client/message_definitions_pb2.py
CLIENT += ./client/message_definitions_pb2_grpc.py
CLIENT += ./client/message_definitions_pb2.pyi

ARTIFACTS += ${CLIENT}

ATTACKS += ./attacks/attack_service_pb2.py
ATTACKS += ./attacks/attack_service_pb2_grpc.py
ATTACKS += ./attacks/attack_service_pb2.pyi

ATTACKS += ./attacks/backend_pb2.py
ATTACKS += ./attacks/backend_pb2_grpc.py
ATTACKS += ./attacks/backend_pb2.pyi

ATTACKS += ./attacks/message_definitions_pb2.py
ATTACKS += ./attacks/message_definitions_pb2_grpc.py
ATTACKS += ./attacks/message_definitions_pb2.pyi

ARTIFACTS += ${ATTACKS}

CLIENT_GEN_PATH = client/
BACKEND_GEN_PATH = backend/
ATTACK_SERVICE_GEN_PATH = attacks/

.PHONY: all
all: ${ARTIFACTS}

./backend/attack_service_pb2.py ./backend/attack_service_pb2_grpc.py ./backend/attack_service_pb2.pyi:
	python3 -m grpc_tools.protoc --proto_path=protos/ --python_out=${BACKEND_GEN_PATH} \
    	--grpc_python_out=${BACKEND_GEN_PATH} --pyi_out=${BACKEND_GEN_PATH} attack_service.proto

./backend/client_pb2.py ./backend/client_pb2_grpc.py ./backend/client_pb2.pyi:
	python3 -m grpc_tools.protoc --proto_path=protos/ --python_out=${BACKEND_GEN_PATH} \
		--grpc_python_out=${BACKEND_GEN_PATH} --pyi_out=${BACKEND_GEN_PATH} client.proto

./backend/backend_pb2.py ./backend/backend_pb2_grpc.py ./backend/backend_pb2.pyi:
	python3 -m grpc_tools.protoc --proto_path=protos/ --python_out=${BACKEND_GEN_PATH} \
		--grpc_python_out=${BACKEND_GEN_PATH} --pyi_out=${BACKEND_GEN_PATH} backend.proto

./backend/message_definitions_pb2.py ./backend/message_definitions_pb2_grpc.py ./backend/message_definitions_pb2.pyi:
	python3 -m grpc_tools.protoc --proto_path=protos/ --python_out=${BACKEND_GEN_PATH} \
		--grpc_python_out=${BACKEND_GEN_PATH} --pyi_out=${BACKEND_GEN_PATH} message_definitions.proto

# ---------------------------------------------------------------------------------------------------------- #

./attacks/attack_service_pb2.py ./attacks/attack_service_pb2_grpc.py ./attacks/attack_service_pb2.pyi:
	python3 -m grpc_tools.protoc --proto_path=protos/ --python_out=${ATTACK_SERVICE_GEN_PATH} \
		--grpc_python_out=${ATTACK_SERVICE_GEN_PATH} --pyi_out=${ATTACK_SERVICE_GEN_PATH} attack_service.proto

./attacks/backend_pb2.py ./attacks/backend_pb2_grpc.py ./attacks/backend_pb2.pyi:
	python3 -m grpc_tools.protoc --proto_path=protos/ --python_out=${ATTACK_SERVICE_GEN_PATH} \
		--grpc_python_out=${ATTACK_SERVICE_GEN_PATH} --pyi_out=${ATTACK_SERVICE_GEN_PATH} backend.proto

./attacks/message_definitions_pb2.py ./attacks/message_definitions_pb2_grpc.py ./attacks/message_definitions_pb2.pyi:
	python3 -m grpc_tools.protoc --proto_path=protos/ --python_out=${ATTACK_SERVICE_GEN_PATH} \
		--grpc_python_out=${ATTACK_SERVICE_GEN_PATH} --pyi_out=${ATTACK_SERVICE_GEN_PATH} message_definitions.proto

# ---------------------------------------------------------------------------------------------------------- #

./client/client_pb2.py ./client/client_pb2_grpc.py ./client/client_pb2.pyi:
	python3 -m grpc_tools.protoc --proto_path=protos/ --python_out=${CLIENT_GEN_PATH} \
		--grpc_python_out=${CLIENT_GEN_PATH} --pyi_out=${CLIENT_GEN_PATH} client.proto

./client/attack_service_pb2.py ./client/attack_service_pb2_grpc.py ./client/attack_service_pb2.pyi:
	python3 -m grpc_tools.protoc --proto_path=protos/ --python_out=${CLIENT_GEN_PATH} \
		--grpc_python_out=${CLIENT_GEN_PATH} --pyi_out=${CLIENT_GEN_PATH} attack_service.proto

./client/backend_pb2.py ./client/backend_pb2_grpc.py ./client/backend_pb2.pyi:
	python3 -m grpc_tools.protoc --proto_path=protos/ --python_out=${CLIENT_GEN_PATH} \
		--grpc_python_out=${CLIENT_GEN_PATH} --pyi_out=${CLIENT_GEN_PATH} backend.proto

./client/message_definitions_pb2.py ./client/message_definitions_pb2_grpc.py ./client/message_definitions_pb2.pyi:
	python3 -m grpc_tools.protoc --proto_path=protos/ --python_out=${CLIENT_GEN_PATH} \
		--grpc_python_out=${CLIENT_GEN_PATH} --pyi_out=${CLIENT_GEN_PATH} message_definitions.proto

# ---------------------------------------------------------------------------------------------------------- #

.PHONY: backend
backend: ${BACKEND}

.PHONY: client
client: ${CLIENT}

.PHONY: attacks
attacks: ${ATTACKS}

.PHONY: clean
clean:
	rm -f ${ARTIFACTS}
	rm -rf ${CLIENT_GEN_PATH}__pycache__
	rm -rf ${ATTACK_SERVICE_GEN_PATH}__pycache__
	rm -rf ${BACKEND_GEN_PATH}__pycache__
