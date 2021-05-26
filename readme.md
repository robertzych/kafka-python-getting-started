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

## ksqlDB

### table-table join
`docker-compose exec ksqldb-cli ksql http://ksqldb-server:8088`
`set 'auto.offset.reset'='earliest';`
TODO: what does this do? Disables caching to get immediate results? What happens if I don't set this?
`set 'cache.max.bytes.buffering'='0';` 
`CREATE TABLE left_table (a VARCHAR PRIMARY KEY, b VARCHAR) WITH (KAFKA_TOPIC='left', KEY_FORMAT='JSON', VALUE_FORMAT='JSON', PARTITIONS=2, REPLICAS=1);`
`CREATE TABLE right_table (c VARCHAR PRIMARY KEY, d VARCHAR) WITH (KAFKA_TOPIC='right', KEY_FORMAT='JSON', VALUE_FORMAT='JSON', PARTITIONS=2, REPLICAS=1);`
`INSERT INTO left_table (a, b) VALUES ('1', 'one');`
`INSERT INTO right_table (c, d) values ('1', 'two');`
`INSERT INTO right_table (c, d) values ('1', 'three');`
`INSERT INTO left_table (a, b) VALUES ('1', 'four');`
`INSERT INTO left_table (a, b) VALUES ('2', 'five');`
`INSERT INTO right_table (c, d) values ('2', 'six');`
`INSERT INTO right_table (c, d) values ('2', 'seven');`
`INSERT INTO left_table (a, b) VALUES ('2', 'eight');`
`SELECT * FROM left_table JOIN right_table ON a=c EMIT CHANGES;`
This output stream produces a result whenever a new event with a matching key is inserted
TODO: show the live results of the output stream side-by-side with the inserts using asciinema

### stream-table join
`DROP TABLE left_table;`
`DROP TABLE right_table;`
`kafka-topics --zookeeper 127.0.0.1 --delete -topic left`
`kafka-topics --zookeeper 127.0.0.1 --delete -topic right`
`CREATE TABLE right_table (c VARCHAR PRIMARY KEY, d VARCHAR) WITH (KAFKA_TOPIC='right', KEY_FORMAT='JSON', VALUE_FORMAT='JSON', PARTITIONS=2, REPLICAS=1);`
`CREATE STREAM left_stream (a VARCHAR KEY, b VARCHAR) WITH (KAFKA_TOPIC='left', KEY_FORMAT='JSON', VALUE_FORMAT='JSON', PARTITIONS=2, REPLICAS=1);`
`INSERT INTO left_stream (a,b) VALUES ('1', 'one');`
`INSERT INTO right_table (c,d) VALUES ('1', 'two');`
`INSERT INTO left_stream (a,b) VALUES ('1', 'three');`
`INSERT INTO left_stream (a,b) VALUES ('1', 'four');`
`INSERT INTO right_table (c,d) VALUES ('2', 'five');`
`INSERT INTO left_stream (a,b) VALUES ('2', 'six');`
`SELECT * FROM left_stream JOIN right_table ON a=c EMIT CHANGES;`
This output stream produces a result whenever a new event arrives in left_stream. The event in left_stream is matched by key to the latest value from right_table.


### stream-stream join
`DROP STREAM left_stream;`
`DROP TABLE right_table;`
`kafka-topics --zookeeper 127.0.0.1 --delete -topic left`
`kafka-topics --zookeeper 127.0.0.1 --delete -topic right`
`CREATE STREAM left_stream (id VARCHAR KEY, value VARCHAR) WITH (KAFKA_TOPIC='left', KEY_FORMAT='JSON', VALUE_FORMAT='JSON', PARTITIONS=2, REPLICAS=1);`
`CREATE STREAM right_stream (id VARCHAR KEY, value VARCHAR) WITH (KAFKA_TOPIC='right', KEY_FORMAT='JSON', VALUE_FORMAT='JSON', PARTITIONS=2, REPLICAS=1);`
`INSERT INTO left_stream (id,value) VALUES ('1', 'one');`
`INSERT INTO right_stream (id,value) VALUES ('1', 'two');`
`INSERT INTO left_stream (id,value) VALUES ('1', 'three');`
`INSERT INTO left_stream (id,value) VALUES ('1', 'four');`
`INSERT INTO right_stream (id,value) VALUES ('2', 'five');`
`INSERT INTO left_stream (id,value) VALUES ('2', 'six');`
`SELECT * FROM left_stream AS l JOIN right_stream AS r WITHIN 5 minutes ON l.id = r.id EMIT CHANGES;`
This output stream produces a result whenever a new event arrives in left_stream. The event in left_stream is matched by key to the latest value from right_table that occurred within the window duration. To see the effects of the window, wait at least 5 minutes, and run...
`INSERT INTO left_stream (id,value) VALUES ('2', 'seven');`
`SELECT * FROM left_stream AS l JOIN right_stream AS r WITHIN 5 minutes ON l.id = r.id EMIT CHANGES;`
Event seven wasn't matched with the latest event in right_stream as the latest event in right_stream is no longer in the window. Now if you immediately run...
INSERT INTO right_stream (id,value) VALUES ('2', 'eight');
`SELECT * FROM left_stream AS l JOIN right_stream AS r WITHIN 5 minutes ON l.id = r.id EMIT CHANGES;`
Event seven is now matching with event eight as now both were captured within the 5 minute window.


## resources
https://github.com/confluentinc/confluent-kafka-python/tree/master/examples
"Temporal-Joins in Kafka Streams and ksqlDB" by Matthias Sax (Kafka Summit Europe 2021)
https://docs.confluent.io/platform/current/quickstart/ce-docker-quickstart.html#step-4-create-and-write-to-a-stream-and-table-using-ksqldb
https://docs.ksqldb.io/en/latest/reference/serialization/
