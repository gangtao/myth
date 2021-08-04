
network:
	docker network create -d bridge pinot-demo
	
batch:
	docker run \
		--network=pinot-demo \
		--name pinot-quickstart \
		-p 9000:9000 \
		-d apachepinot/pinot:latest QuickStart \
		-type batch

stream:
	docker run \
		--network=pinot-demo \
		--name pinot-quickstart \
		-p 9000:9000 \
		-d apachepinot/pinot:latest QuickStart \
		-type stream

hybrid:
	docker run \
		--network=pinot-demo \
		--name pinot-quickstart \
		-p 9000:9000 \
		-d apachepinot/pinot:latest QuickStart \
		-type hybrid