#!/bin/sh

LOCAL_GEN_PATH="./"
mkdir -p $LOCAL_GEN_PATH
python3 -m grpc_tools.protoc --proto_path=protos/ --python_out=$LOCAL_GEN_PATH \
    --grpc_python_out=$LOCAL_GEN_PATH --pyi_out=$LOCAL_GEN_PATH attack_service_api.proto
python3 -m grpc_tools.protoc --proto_path=protos/ --python_out=$LOCAL_GEN_PATH \
    --grpc_python_out=$LOCAL_GEN_PATH --pyi_out=$LOCAL_GEN_PATH client_api.proto
python3 -m grpc_tools.protoc --proto_path=protos/ --python_out=$LOCAL_GEN_PATH \
    --grpc_python_out=$LOCAL_GEN_PATH --pyi_out=$LOCAL_GEN_PATH backend_api.proto
python3 -m grpc_tools.protoc --proto_path=protos/ --python_out=$LOCAL_GEN_PATH \
    --grpc_python_out=$LOCAL_GEN_PATH --pyi_out=$LOCAL_GEN_PATH message_definitions.proto

ATTACK_SERVICE_GEN_PATH="attacks/"
mkdir -p $ATTACK_SERVICE_GEN_PATH
python3 -m grpc_tools.protoc --proto_path=protos/ --python_out=$ATTACK_SERVICE_GEN_PATH \
    --grpc_python_out=$ATTACK_SERVICE_GEN_PATH --pyi_out=$ATTACK_SERVICE_GEN_PATH attack_service_api.proto
python3 -m grpc_tools.protoc --proto_path=protos/ --python_out=$ATTACK_SERVICE_GEN_PATH \
    --grpc_python_out=$ATTACK_SERVICE_GEN_PATH --pyi_out=$ATTACK_SERVICE_GEN_PATH message_definitions.proto
python3 -m grpc_tools.protoc --proto_path=protos/ --python_out=$ATTACK_SERVICE_GEN_PATH \
    --grpc_python_out=$ATTACK_SERVICE_GEN_PATH --pyi_out=$ATTACK_SERVICE_GEN_PATH backend_api.proto
