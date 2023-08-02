# Regenerates all generated files in the Python examples directory.

BACKEND=

BACKEND += ./attack_service_api_pb2.py
BACKEND += ./attack_service_api_pb2_grpc.py
BACKEND += ./attack_service_api_pb2.pyi

BACKEND += ./client_api_pb2.py
BACKEND += ./client_api_pb2_grpc.py
BACKEND += ./client_api_pb2.pyi

BACKEND += ./backend_api_pb2.py
BACKEND += ./backend_api_pb2_grpc.py
BACKEND += ./backend_api_pb2.pyi

BACKEND += ./message_definitions_pb2.py
BACKEND += ./message_definitions_pb2_grpc.py
BACKEND += ./message_definitions_pb2.pyi

ARTIFACTS=

ARTIFACTS += ./attack_service_api_pb2.py
ARTIFACTS += ./attack_service_api_pb2_grpc.py
ARTIFACTS += ./attack_service_api_pb2.pyi

ARTIFACTS += ./client_api_pb2.py
ARTIFACTS += ./client_api_pb2_grpc.py
ARTIFACTS += ./client_api_pb2.pyi

ARTIFACTS += ./backend_api_pb2.py
ARTIFACTS += ./backend_api_pb2_grpc.py
ARTIFACTS += ./backend_api_pb2.pyi

ARTIFACTS += ./message_definitions_pb2.py
ARTIFACTS += ./message_definitions_pb2_grpc.py
ARTIFACTS += ./message_definitions_pb2.pyi

ARTIFACTS += ./attacks/attack_service_api_pb2.py
ARTIFACTS += ./attacks/attack_service_api_pb2_grpc.py
ARTIFACTS += ./attacks/attack_service_api_pb2.pyi

ARTIFACTS += ./attacks/backend_api_pb2.py
ARTIFACTS += ./attacks/backend_api_pb2_grpc.py
ARTIFACTS += ./attacks/backend_api_pb2.pyi

ARTIFACTS += ./attacks/message_definitions_pb2.py
ARTIFACTS += ./attacks/message_definitions_pb2_grpc.py
ARTIFACTS += ./attacks/message_definitions_pb2.pyi

LOCAL_GEN_PATH="./"
ATTACK_SERVICE_GEN_PATH="attacks/"

.PHONY: all
all: ${ARTIFACTS}

./attack_service_api_pb2.py ./attack_service_api_pb2_grpc.py ./attack_service_api_pb2.pyi:
	python3 -m grpc_tools.protoc --proto_path=protos/ --python_out=${LOCAL_GEN_PATH} \
    	--grpc_python_out=${LOCAL_GEN_PATH} --pyi_out=${LOCAL_GEN_PATH} attack_service_api.proto

./client_api_pb2.py ./client_api_pb2_grpc.py ./client_api_pb2.pyi:
	python3 -m grpc_tools.protoc --proto_path=protos/ --python_out=${LOCAL_GEN_PATH} \
		--grpc_python_out=${LOCAL_GEN_PATH} --pyi_out=${LOCAL_GEN_PATH} client_api.proto

./backend_api_pb2.py ./backend_api_pb2_grpc.py ./backend_api_pb2.pyi:
	python3 -m grpc_tools.protoc --proto_path=protos/ --python_out=${LOCAL_GEN_PATH} \
		--grpc_python_out=${LOCAL_GEN_PATH} --pyi_out=${LOCAL_GEN_PATH} backend_api.proto

./message_definitions_pb2.py ./message_definitions_pb2_grpc.py ./message_definitions_pb2.pyi:
	python3 -m grpc_tools.protoc --proto_path=protos/ --python_out=${LOCAL_GEN_PATH} \
		--grpc_python_out=${LOCAL_GEN_PATH} --pyi_out=${LOCAL_GEN_PATH} message_definitions.proto


./attacks/attack_service_api_pb2.py ./attacks/attack_service_api_pb2_grpc.py ./attacks/attack_service_api_pb2.pyi:
	python3 -m grpc_tools.protoc --proto_path=protos/ --python_out=${ATTACK_SERVICE_GEN_PATH} \
		--grpc_python_out=${ATTACK_SERVICE_GEN_PATH} --pyi_out=${ATTACK_SERVICE_GEN_PATH} attack_service_api.proto

./attacks/backend_api_pb2.py ./attacks/backend_api_pb2_grpc.py ./attacks/backend_api_pb2.pyi:
	python3 -m grpc_tools.protoc --proto_path=protos/ --python_out=${ATTACK_SERVICE_GEN_PATH} \
		--grpc_python_out=${ATTACK_SERVICE_GEN_PATH} --pyi_out=${ATTACK_SERVICE_GEN_PATH} backend_api.proto

./attacks/message_definitions_pb2.py ./attacks/message_definitions_pb2_grpc.py ./attacks/message_definitions_pb2.pyi:
	python3 -m grpc_tools.protoc --proto_path=protos/ --python_out=${ATTACK_SERVICE_GEN_PATH} \
		--grpc_python_out=${ATTACK_SERVICE_GEN_PATH} --pyi_out=${ATTACK_SERVICE_GEN_PATH} message_definitions.proto

.PHONY: backend
backend: ${BACKEND}

.PHONY: clean
clean:
	rm -f ${ARTIFACTS}
