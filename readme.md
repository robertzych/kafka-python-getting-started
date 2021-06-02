# kafka-python-getting-started

## kafka setup
docker-compose up -d

To list all the kafka-* cli tools:  
docker exec -it broker bash  
ls /bin | grep kafka-  


## python setup
brew install pipenv  
pipenv install


## json examples
To create a topic with schema validation enabled:
docker exec -it broker kafka-topics --create --bootstrap-server localhost:9092 --replication-factor 1 \
--partitions 1 --topic user_json \
--config confluent.value.schema.validation=true  

export PYTHONPATH="${PYTHONPATH}:${PWD}"  
pipenv run python examples/json/producing_json.py  
pipenv run python examples/json/consuming_json.py  
press ctrl+c to close consuming_json.py  
Add "required_field" to the required list on producing_json.py:39  
pipenv run python examples/json/producing_json.py  
The following error is expected:
confluent_kafka.error.ValueSerializationError: KafkaError{code=_VALUE_SERIALIZATION,val=-161,str="Schema being registered is incompatible with an earlier schema for subject "user_json-value" (HTTP status code 409, SR code 409)"}


## protobuf examples
docker exec -it broker kafka-topics --create --bootstrap-server localhost:9092 --replication-factor 1 \
--partitions 1 --topic mytopic_protobuf \
--config confluent.value.schema.validation=true

export PYTHONPATH="${PYTHONPATH}:${PWD}"  
pipenv run python examples/protobuf/producing_protobuf.py  
pipenv run python examples/protobuf/consuming_protobuf.py  
press ctrl+c to close consuming_protobuf.py  

To generate python classes from protobuf (.proto) files:  
brew install protobuf  # installs the protobuf compiler (protoc)  
protoc -I=. --python_out=. ./user.proto    # generates user_pb2.py from user.proto


## ksqlDB examples

### table-table join
docker-compose exec ksqldb-cli ksql http://ksqldb-server:8088  

CREATE TABLE left_table (a VARCHAR PRIMARY KEY, b VARCHAR) WITH (KAFKA_TOPIC='left', KEY_FORMAT='JSON', VALUE_FORMAT='JSON', PARTITIONS=2, REPLICAS=1);  
CREATE TABLE right_table (c VARCHAR PRIMARY KEY, d VARCHAR) WITH (KAFKA_TOPIC='right', KEY_FORMAT='JSON', VALUE_FORMAT='JSON', PARTITIONS=2, REPLICAS=1);  
CREATE TABLE TT_JOIN AS SELECT * FROM left_table JOIN right_table ON a=c EMIT CHANGES;  
SELECT * FROM TT_JOIN EMIT CHANGES;  
Using the `CREATE TABLE AS SELECT` syntax we’ve generated a new table that is updated whenever a new record with a matching key is inserted.  

To observe the live updates, open a new window a run the following inserts one statement at a time.
docker-compose exec ksqldb-cli ksql http://ksqldb-server:8088  
INSERT INTO left_table (a, b) VALUES ('1', 'one');  
INSERT INTO right_table (c, d) values ('1', 'two');  
INSERT INTO right_table (c, d) values ('1', 'three');  
INSERT INTO left_table (a, b) VALUES ('1', 'four');  
INSERT INTO left_table (a, b) VALUES ('2', 'five');  
INSERT INTO right_table (c, d) values ('2', 'six');  
INSERT INTO right_table (c, d) values ('2', 'seven');  
INSERT INTO left_table (a, b) VALUES ('2', 'eight');  

Cleaning up...  
Press ctrl+c in the first window to terminate the query.  
TERMINATE CTAS_TT_JOIN_5;  
DROP TABLE TT_JOIN;  
DROP TABLE left_table;  
DROP TABLE right_table;  
exit  
docker exec -it broker kafka-topics --zookeeper zookeeper --delete -topic left  
docker exec -it broker kafka-topics --zookeeper zookeeper --delete -topic right


### stream-table join
docker-compose exec ksqldb-cli ksql http://ksqldb-server:8088  

CREATE STREAM left_stream (a VARCHAR KEY, b VARCHAR) WITH (KAFKA_TOPIC='left', KEY_FORMAT='JSON', VALUE_FORMAT='JSON', PARTITIONS=2, REPLICAS=1);  
CREATE TABLE right_table (c VARCHAR PRIMARY KEY, d VARCHAR) WITH (KAFKA_TOPIC='right', KEY_FORMAT='JSON', VALUE_FORMAT='JSON', PARTITIONS=2, REPLICAS=1);  
CREATE STREAM ST_JOIN AS SELECT * FROM left_stream JOIN right_table ON a=c EMIT CHANGES;  
SELECT * FROM ST_JOIN EMIT CHANGES;  
Using the `CREATE STREAM AS SELECT` syntax we've generated a new stream that produces a result whenever a new event arrives in left_stream.  
The event in left_stream is matched by key to the latest value from right_table.

To observe the live updates, open a new window a run the following inserts one statement at a time.  
docker-compose exec ksqldb-cli ksql http://ksqldb-server:8088  
INSERT INTO left_stream (a,b) VALUES ('1', 'one');  
INSERT INTO right_table (c,d) VALUES ('1', 'two');  
INSERT INTO left_stream (a,b) VALUES ('1', 'three');  
INSERT INTO left_stream (a,b) VALUES ('1', 'four');  
INSERT INTO right_table (c,d) VALUES ('2', 'five');  
INSERT INTO left_stream (a,b) VALUES ('2', 'six');

Cleaning up...  
Press ctrl+c in the first window to terminate the query.  
TERMINATE CSAS_ST_JOIN_17;  
DROP STREAM ST_JOIN;  
DROP STREAM left_stream;  
DROP TABLE right_table;  
exit  
docker exec -it broker kafka-topics --zookeeper zookeeper --delete -topic left  
docker exec -it broker kafka-topics --zookeeper zookeeper --delete -topic right

### stream-stream join
docker-compose exec ksqldb-cli ksql http://ksqldb-server:8088  
CREATE STREAM left_stream (id VARCHAR KEY, value VARCHAR) WITH (KAFKA_TOPIC='left', KEY_FORMAT='JSON', VALUE_FORMAT='JSON', PARTITIONS=2, REPLICAS=1);  
CREATE STREAM right_stream (id VARCHAR KEY, value VARCHAR) WITH (KAFKA_TOPIC='right', KEY_FORMAT='JSON', VALUE_FORMAT='JSON', PARTITIONS=2, REPLICAS=1);  
CREATE STREAM SS_JOIN AS SELECT * FROM left_stream AS l JOIN right_stream AS r WITHIN 1 minute ON l.id = r.id EMIT CHANGES;  
SELECT * FROM SS_JOIN EMIT CHANGES;  
This output stream produces a result whenever a new event arrives in left_stream.  
The event in left_stream is matched by key to the latest value from right_table that occurred within the window duration.  
To see the effects of the window, wait at least 1 minute between executing a subsequent insert statement.

In a new window a run the following inserts one statement at a time.  
docker-compose exec ksqldb-cli ksql http://ksqldb-server:8088  
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
Press ctrl+c in the first window to terminate the query.  
TERMINATE CSAS_SS_JOIN_35;  
DROP STREAM SS_JOIN;  
DROP STREAM left_stream;  
DROP STREAM right_stream;  
exit  
docker exec -it broker kafka-topics --zookeeper zookeeper --delete -topic left  
docker exec -it broker kafka-topics --zookeeper zookeeper --delete -topic right  


## resources
https://developers.google.com/protocol-buffers/docs/pythontutorial  
https://docs.confluent.io/platform/current/quickstart/ce-docker-quickstart.html#step-4-create-and-write-to-a-stream-and-table-using-ksqldb  
https://docs.ksqldb.io/en/latest/  
"Temporal-Joins in Kafka Streams and ksqlDB" by Matthias Sax (Kafka Summit Europe 2021)  
