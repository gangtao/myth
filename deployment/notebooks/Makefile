BIN_NAME ?= notebooks
VERSION ?= 0.1
IMAGE_NAME ?= $(BIN_NAME):$(VERSION)
DOCKER_ID_USER ?= naughtytao

FULLNAME=$(DOCKER_ID_USER)/${BIN_NAME}:${VERSION}

PWD=$(shell pwd)

docker: Dockerfile
	docker build -t $(IMAGE_NAME) .

push:
	docker tag $(IMAGE_NAME) ${FULLNAME}
	docker push ${FULLNAME}

run_ck:
	docker run --network clickhouse_default -p 8888:8888 -v $(PWD)/notebooks/:/opt/notebooks/ $(IMAGE_NAME) --NotebookApp.token=''

run_qeustdb:
	docker run --network questdb_default -p 8888:8888 -v $(PWD)/notebooks/:/opt/notebooks/ $(IMAGE_NAME) --NotebookApp.token=''

run:
	docker run -p 8888:8888 -v $(PWD)/notebooks/:/opt/notebooks/ $(IMAGE_NAME) --NotebookApp.token=''