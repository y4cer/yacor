# Regenerates all generated files in the Python examples directory.

BACKEND=

BACKEND += ./attack_service_pb2.py
BACKEND += ./attack_service_pb2_grpc.py
BACKEND += ./attack_service_pb2.pyi

BACKEND += ./client_pb2.py
BACKEND += ./client_pb2_grpc.py
BACKEND += ./client_pb2.pyi

BACKEND += ./backend_pb2.py
BACKEND += ./backend_pb2_grpc.py
BACKEND += ./backend_pb2.pyi

BACKEND += ./message_definitions_pb2.py
BACKEND += ./message_definitions_pb2_grpc.py
BACKEND += ./message_definitions_pb2.pyi

ARTIFACTS=

ARTIFACTS += ./attack_service_pb2.py
ARTIFACTS += ./attack_service_pb2_grpc.py
ARTIFACTS += ./attack_service_pb2.pyi

ARTIFACTS += ./client_pb2.py
ARTIFACTS += ./client_pb2_grpc.py
ARTIFACTS += ./client_pb2.pyi

ARTIFACTS += ./backend_pb2.py
ARTIFACTS += ./backend_pb2_grpc.py
ARTIFACTS += ./backend_pb2.pyi

ARTIFACTS += ./message_definitions_pb2.py
ARTIFACTS += ./message_definitions_pb2_grpc.py
ARTIFACTS += ./message_definitions_pb2.pyi

ARTIFACTS += ./attacks/attack_service_pb2.py
ARTIFACTS += ./attacks/attack_service_pb2_grpc.py
ARTIFACTS += ./attacks/attack_service_pb2.pyi

ARTIFACTS += ./attacks/backend_pb2.py
ARTIFACTS += ./attacks/backend_pb2_grpc.py
ARTIFACTS += ./attacks/backend_pb2.pyi

ARTIFACTS += ./attacks/message_definitions_pb2.py
ARTIFACTS += ./attacks/message_definitions_pb2_grpc.py
ARTIFACTS += ./attacks/message_definitions_pb2.pyi

ARTIFACTS += ./attacks/client_pb2.py
ARTIFACTS += ./attacks/client_pb2_grpc.py
ARTIFACTS += ./attacks/client_pb2.pyi

LOCAL_GEN_PATH="./"
ATTACK_SERVICE_GEN_PATH="attacks/"

.PHONY: all
all: ${ARTIFACTS}

./attack_service_pb2.py ./attack_service_pb2_grpc.py ./attack_service_pb2.pyi:
	python3 -m grpc_tools.protoc --proto_path=protos/ --python_out=${LOCAL_GEN_PATH} \
    	--grpc_python_out=${LOCAL_GEN_PATH} --pyi_out=${LOCAL_GEN_PATH} attack_service.proto

./client_pb2.py ./client_pb2_grpc.py ./client_pb2.pyi:
	python3 -m grpc_tools.protoc --proto_path=protos/ --python_out=${LOCAL_GEN_PATH} \
		--grpc_python_out=${LOCAL_GEN_PATH} --pyi_out=${LOCAL_GEN_PATH} client.proto

./backend_pb2.py ./backend_pb2_grpc.py ./backend_pb2.pyi:
	python3 -m grpc_tools.protoc --proto_path=protos/ --python_out=${LOCAL_GEN_PATH} \
		--grpc_python_out=${LOCAL_GEN_PATH} --pyi_out=${LOCAL_GEN_PATH} backend.proto

./message_definitions_pb2.py ./message_definitions_pb2_grpc.py ./message_definitions_pb2.pyi:
	python3 -m grpc_tools.protoc --proto_path=protos/ --python_out=${LOCAL_GEN_PATH} \
		--grpc_python_out=${LOCAL_GEN_PATH} --pyi_out=${LOCAL_GEN_PATH} message_definitions.proto


./attacks/attack_service_pb2.py ./attacks/attack_service_pb2_grpc.py ./attacks/attack_service_pb2.pyi:
	python3 -m grpc_tools.protoc --proto_path=protos/ --python_out=${ATTACK_SERVICE_GEN_PATH} \
		--grpc_python_out=${ATTACK_SERVICE_GEN_PATH} --pyi_out=${ATTACK_SERVICE_GEN_PATH} attack_service.proto

./attacks/backend_pb2.py ./attacks/backend_pb2_grpc.py ./attacks/backend_pb2.pyi:
	python3 -m grpc_tools.protoc --proto_path=protos/ --python_out=${ATTACK_SERVICE_GEN_PATH} \
		--grpc_python_out=${ATTACK_SERVICE_GEN_PATH} --pyi_out=${ATTACK_SERVICE_GEN_PATH} backend.proto

./attacks/message_definitions_pb2.py ./attacks/message_definitions_pb2_grpc.py ./attacks/message_definitions_pb2.pyi:
	python3 -m grpc_tools.protoc --proto_path=protos/ --python_out=${ATTACK_SERVICE_GEN_PATH} \
		--grpc_python_out=${ATTACK_SERVICE_GEN_PATH} --pyi_out=${ATTACK_SERVICE_GEN_PATH} message_definitions.proto

./attacks/client_pb2.py ./attacks/client_pb2_grpc.py ./attacks/client_pb2.pyi:
	python3 -m grpc_tools.protoc --proto_path=protos/ --python_out=${ATTACK_SERVICE_GEN_PATH} \
		--grpc_python_out=${ATTACK_SERVICE_GEN_PATH} --pyi_out=${ATTACK_SERVICE_GEN_PATH} client.proto

.PHONY: backend
backend: ${BACKEND}

.PHONY: clean
clean:
	rm -f ${ARTIFACTS}
	rm -rf __pycache__
