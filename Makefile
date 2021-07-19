BIN_NAME ?= myth
VERSION ?= 0.1
IMAGE_NAME ?= $(BIN_NAME):$(VERSION)
DOCKER_ID_USER ?= naughtytao

DATE=$(shell date '+%Y%m%d')

FULLNAME=$(DOCKER_ID_USER)/${IMAGE_NAME}.${DATE}

PWD=$(shell pwd)

.PHONY: docker

all: install build docker
	docker-compose up -d

docker: Dockerfile
	docker build -t $(IMAGE_NAME) .

push:
	docker tag $(IMAGE_NAME) $(FULLNAME)
	docker push $(FULLNAME)

test:
	docker run -v $(PWD)/src:/app $(IMAGE_NAME) pytest -s

debug_clickhouse:
	docker run --network clickhouse_default -v $(PWD)/src:/app $(IMAGE_NAME) python3 -m myth.main --config clickhouse.json

debug_influx:
	docker run --network influxdb_default -v $(PWD)/src:/app $(IMAGE_NAME) python3 -m myth.main --config influx.json

run:
	docker run $(IMAGE_NAME) python3 -m myth.main --help

