
#kubectl --namespace kafka port-forward $POD_NAME 8080:80
install-ui:
	helm install kafka-ui kafka-ui/kafka-ui --version 0.0.1 -n kafka --set envs.config.KAFKA_CLUSTERS_0_NAME=local --set envs.config.KAFKA_CLUSTERS_0_BOOTSTRAPSERVERS=my-kafka:9092
	helm repo add main https://bedag.github.io/helm-charts/
	helm install my-kafdrop main/kafdrop -n kafka --version 0.2.3 --set config.kafka.connections[0]=my-kafka:9092
	helm repo add stable https://charts.helm.sh/stable

forward:
	kubectl -n kafka port-forward kafka-ui-566947d896-tsh9q 8888:8080

start:
	docker-compose up -d
