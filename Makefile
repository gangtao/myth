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
	docker run --network influxdb1_default -v $(PWD)/src:/app $(IMAGE_NAME) python3 -m myth.main --config influx.json

debug_influx2:
	docker run --network influxdb2_default -v $(PWD)/src:/app $(IMAGE_NAME) python3 -m myth.main --config influx2.json

debug_td:
	docker run --network tdengine_default -v $(PWD)/src:/app $(IMAGE_NAME) python3 -m myth.main --config tdengine.json

debug_questdb:
	docker run --network questdb_default -v $(PWD)/src:/app $(IMAGE_NAME) python3 -m myth.main --config questdb.json

run:
	docker run $(IMAGE_NAME) python3 -m myth.main --help

