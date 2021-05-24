# kafka-python-getting-started

## kafka
`docker-compose up -d`

`docker exec -it broker bash`, kafka-{tab completion}

`kafka-topics --zookeeper 127.0.0.1 --create -topic mytopic --partitions 6 --replication-factor 1`
`kafka-console-consumer --bootstrap-server 127.0.0.1:9092 --topic mytopic`

`kafka-topics --zookeeper 127.0.0.1 --create -topic mytopic_protobuf --partitions 6 --replication-factor 1`
`kafka-protobuf-console-consumer --bootstrap-server 127.0.0.1:9092 --topic mytopic_protobuf --from-beginning --property schema.registry.url=http://localhost:8081`

`kafka-topics --zookeeper 127.0.0.1 --create -topic twitter_tweets_protobuf --partitions 6 --replication-factor 1`
`kafka-protobuf-console-consumer --bootstrap-server 127.0.0.1:9092 --topic twitter_tweets_protobuf --from-beginning --property schema.registry.url=http://localhost:8081`


## python
`pip3 install pipenv`  # installs pipenv
`pipenv --three`  # creates Pipfile
`pipenv run python -V`  # reports python version used in venv
`pipenv install confluent-kafka`  # install the latest version (1.7.0)
`pipenv install requests`  # required to use schema registry
`pipenv install jsonschema`
`pipenv install protobuf`
`pipenv run pip list`  # reports all packages+versions used in venv


## json
`docker exec -it broker kafka-topics --create --bootstrap-server localhost:9092 --replication-factor 1 \
--partitions 1 --topic user_json \
--config confluent.value.schema.validation=true`
`docker exec -it broker kafka-consumer-groups --bootstrap-server localhost:9092 --group json-consumer-group-1 --delete-offsets --execute --topic user_json`
confluent_kafka.error.ValueDeserializationError: KafkaError{code=_VALUE_DESERIALIZATION,val=-159,str="'twitter_handle' is a required property"}
`docker exec -it broker kafka-topics --delete --bootstrap-server localhost:9092 \
--topic user_json`
When adding a new required field to an existing schema:
confluent_kafka.error.ValueSerializationError: KafkaError{code=_VALUE_SERIALIZATION,val=-161,str="Schema being registered is incompatible with an earlier schema for subject "user_json-value" (HTTP status code 409, SR code 409)"}



## protobuf
to regenerate protobuf classes you ust first install the protobuf compiler (protoc)
https://developers.google.com/protocol-buffers/docs/pythontutorial
https://github.com/protocolbuffers/protobuf#protocol-compiler-installation
To install protoc:`brew install protobuf` 
Or to upgrade protoc: `brew upgrade protobuf`
`protoc --version`  # reports libprotoc 3.17.0
`protoc -I=. --python_out=. ./user.proto`

`kafka-consumer-groups --bootstrap-server localhost:9092 --group consumer-group-1 --delete-offsets --execute --topic mytopic_protobuf`
`kafka-consumer-groups --bootstrap-server localhost:9092 --group consumer-group-1 --describe`

### create topic with schema validation
`docker exec -it broker kafka-topics --create --bootstrap-server localhost:9092 --replication-factor 1 \
--partitions 1 --topic mytopic_protobuf \
--config confluent.value.schema.validation=true`

### alter topic with schema validation
`kafka-configs --bootstrap-server localhost:9092 --alter --entity-type topics --entity-name mytopic_protobuf --add-config confluent.value.schema.validation=true`

## resources
https://github.com/confluentinc/confluent-kafka-python/tree/master/examples
