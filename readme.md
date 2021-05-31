# kafka-python-getting-started

## kafka
docker-compose up -d

docker exec -it broker bash, kafka-{tab completion}

kafka-topics --zookeeper 127.0.0.1 --create -topic mytopic --partitions 6 --replication-factor 1
kafka-console-consumer --bootstrap-server 127.0.0.1:9092 --topic mytopic

kafka-topics --zookeeper 127.0.0.1 --create -topic mytopic_protobuf --partitions 6 --replication-factor 1
kafka-protobuf-console-consumer --bootstrap-server 127.0.0.1:9092 --topic mytopic_protobuf --from-beginning --property schema.registry.url=http://localhost:8081

kafka-topics --zookeeper 127.0.0.1 --create -topic twitter_tweets_protobuf --partitions 6 --replication-factor 1
kafka-protobuf-console-consumer --bootstrap-server 127.0.0.1:9092 --topic twitter_tweets_protobuf --from-beginning --property schema.registry.url=http://localhost:8081


## python
pip3 install pipenv  # installs pipenv
pipenv --three  # creates Pipfile
pipenv run python -V  # reports python version used in venv
pipenv install confluent-kafka  # install the latest version (1.7.0)
pipenv install requests  # required to use schema registry
pipenv install jsonschema
pipenv install protobuf
pipenv run pip list  # reports all packages+versions used in venv


## json
docker exec -it broker kafka-topics --create --bootstrap-server localhost:9092 --replication-factor 1 \
--partitions 1 --topic user_json \
--config confluent.value.schema.validation=true
docker exec -it broker kafka-consumer-groups --bootstrap-server localhost:9092 --group json-consumer-group-1 --delete-offsets --execute --topic user_json
confluent_kafka.error.ValueDeserializationError: KafkaError{code=_VALUE_DESERIALIZATION,val=-159,str="'twitter_handle' is a required property"}
docker exec -it broker kafka-topics --delete --bootstrap-server localhost:9092 \
--topic user_json
When adding a new required field to an existing schema:
confluent_kafka.error.ValueSerializationError: KafkaError{code=_VALUE_SERIALIZATION,val=-161,str="Schema being registered is incompatible with an earlier schema for subject "user_json-value" (HTTP status code 409, SR code 409)"}



## protobuf
to regenerate protobuf classes you ust first install the protobuf compiler (protoc)
https://developers.google.com/protocol-buffers/docs/pythontutorial
https://github.com/protocolbuffers/protobuf#protocol-compiler-installation
To install protoc:brew install protobuf 
Or to upgrade protoc: brew upgrade protobuf
protoc --version  # reports libprotoc 3.17.0
protoc -I=. --python_out=. ./user.proto

kafka-consumer-groups --bootstrap-server localhost:9092 --group consumer-group-1 --delete-offsets --execute --topic mytopic_protobuf
kafka-consumer-groups --bootstrap-server localhost:9092 --group consumer-group-1 --describe

### create topic with schema validation
docker exec -it broker kafka-topics --create --bootstrap-server localhost:9092 --replication-factor 1 \
--partitions 1 --topic mytopic_protobuf \
--config confluent.value.schema.validation=true

### alter topic with schema validation
kafka-configs --bootstrap-server localhost:9092 --alter --entity-type topics --entity-name mytopic_protobuf --add-config confluent.value.schema.validation=true

## ksqlDB

### table-table join
docker-compose exec ksqldb-cli ksql http://ksqldb-server:8088  
set 'auto.offset.reset'='earliest';  

CREATE TABLE left_table (a VARCHAR PRIMARY KEY, b VARCHAR) WITH (KAFKA_TOPIC='left', KEY_FORMAT='JSON', VALUE_FORMAT='JSON', PARTITIONS=2, REPLICAS=1);  
CREATE TABLE right_table (c VARCHAR PRIMARY KEY, d VARCHAR) WITH (KAFKA_TOPIC='right', KEY_FORMAT='JSON', VALUE_FORMAT='JSON', PARTITIONS=2, REPLICAS=1);  
CREATE TABLE TT_JOIN AS SELECT * FROM left_table JOIN right_table ON a=c EMIT CHANGES;  

SELECT * FROM TT_JOIN EMIT CHANGES;  
Using the `CREATE TABLE AS SELECT` syntax we’ve generated a new table that is updated whenever a new record with a matching key is inserted.

To observe the live updates, open a new window a run the following inserts one statement at a time.  
INSERT INTO left_table (a, b) VALUES ('1', 'one');  
INSERT INTO right_table (c, d) values ('1', 'two');  
INSERT INTO right_table (c, d) values ('1', 'three');  
INSERT INTO left_table (a, b) VALUES ('1', 'four');  
INSERT INTO left_table (a, b) VALUES ('2', 'five');  
INSERT INTO right_table (c, d) values ('2', 'six');  
INSERT INTO right_table (c, d) values ('2', 'seven');  
INSERT INTO left_table (a, b) VALUES ('2', 'eight');  

TERMINATE CTAS_TT_JOIN_5;  
DROP TABLE TT_JOIN;  
DROP TABLE left_table;  
DROP TABLE right_table;  
docker exec -it broker kafka-topics --zookeeper zookeeper --delete -topic left  
docker exec -it broker kafka-topics --zookeeper zookeeper --delete -topic right


### stream-table join
CREATE STREAM left_stream (a VARCHAR KEY, b VARCHAR) WITH (KAFKA_TOPIC='left', KEY_FORMAT='JSON', VALUE_FORMAT='JSON', PARTITIONS=2, REPLICAS=1);  
CREATE TABLE right_table (c VARCHAR PRIMARY KEY, d VARCHAR) WITH (KAFKA_TOPIC='right', KEY_FORMAT='JSON', VALUE_FORMAT='JSON', PARTITIONS=2, REPLICAS=1);  

CREATE STREAM ST_JOIN AS SELECT * FROM left_stream JOIN right_table ON a=c EMIT CHANGES;  
SELECT * FROM ST_JOIN EMIT CHANGES;  
Using the `CREATE STREAM AS SELECT` syntax we've generated a new stream that produces a result whenever a new event arrives in left_stream. 
The event in left_stream is matched by key to the latest value from right_table.

To observe the live updates, open a new window a run the following inserts one statement at a time.  
INSERT INTO left_stream (a,b) VALUES ('1', 'one');  
INSERT INTO right_table (c,d) VALUES ('1', 'two');  
INSERT INTO left_stream (a,b) VALUES ('1', 'three');  
INSERT INTO left_stream (a,b) VALUES ('1', 'four');  
INSERT INTO right_table (c,d) VALUES ('2', 'five');  
INSERT INTO left_stream (a,b) VALUES ('2', 'six');

TERMINATE CSAS_ST_JOIN_17;  
DROP STREAM ST_JOIN;  
DROP STREAM left_stream;  
DROP TABLE right_table;  
docker exec -it broker kafka-topics --zookeeper zookeeper --delete -topic left  
docker exec -it broker kafka-topics --zookeeper zookeeper --delete -topic right


### stream-stream join
CREATE STREAM left_stream (id VARCHAR KEY, value VARCHAR) WITH (KAFKA_TOPIC='left', KEY_FORMAT='JSON', VALUE_FORMAT='JSON', PARTITIONS=2, REPLICAS=1);  
CREATE STREAM right_stream (id VARCHAR KEY, value VARCHAR) WITH (KAFKA_TOPIC='right', KEY_FORMAT='JSON', VALUE_FORMAT='JSON', PARTITIONS=2, REPLICAS=1);  

CREATE STREAM SS_JOIN AS SELECT * FROM left_stream AS l JOIN right_stream AS r WITHIN 1 minute ON l.id = r.id EMIT CHANGES;  
SELECT * FROM SS_JOIN EMIT CHANGES;   
This output stream produces a result whenever a new event arrives in left_stream. 
The event in left_stream is matched by key to the latest value from right_table that occurred within the window duration. 
To see the effects of the window, wait at least 1 minute between executing a subsequent insert statement.

In a new window a run the following inserts one statement at a time.  
INSERT INTO left_stream (id,value) VALUES ('1', 'one');  
INSERT INTO right_stream (id,value) VALUES ('1', 'two');  
INSERT INTO left_stream (id,value) VALUES ('1', 'three');  
INSERT INTO left_stream (id,value) VALUES ('1', 'four');  
INSERT INTO right_stream (id,value) VALUES ('2', 'five');  
INSERT INTO left_stream (id,value) VALUES ('2', 'six');  
Wait 1 minute  
INSERT INTO left_stream (id,value) VALUES ('2', 'seven');  
Event seven wasn't matched with the latest event in right_stream as the latest event in right_stream is no longer in the window.   
Now if you immediately run...  
INSERT INTO right_stream (id,value) VALUES ('2', 'eight');  
Event seven is now matching with event eight as now both were captured within the 1-minute window.

Cleaning up...  
TERMINATE CSAS_SS_JOIN_35;  
DROP STREAM SS_JOIN;  
DROP STREAM left_stream;  
DROP STREAM right_stream;  
exit  
docker exec -it broker kafka-topics --zookeeper zookeeper --delete -topic left  
docker exec -it broker kafka-topics --zookeeper zookeeper --delete -topic right  


## resources
https://github.com/confluentinc/confluent-kafka-python/tree/master/examples
https://docs.confluent.io/platform/current/quickstart/ce-docker-quickstart.html#step-4-create-and-write-to-a-stream-and-table-using-ksqldb
https://docs.ksqldb.io/en/latest/  
"Temporal-Joins in Kafka Streams and ksqlDB" by Matthias Sax (Kafka Summit Europe 2021)
