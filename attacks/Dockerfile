FROM python:3.11

WORKDIR /app

ENV PYTHONUNBUFFERED=1\
    PYTHONPATH="."

COPY requirements.txt .
RUN pip3 install --upgrade -r requirements.txt

COPY protos protos/
COPY Makefile .
COPY attacks/ ./attacks/

RUN make clean && make all
