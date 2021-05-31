from uuid import uuid4

from confluent_kafka import SerializingProducer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.json_schema import JSONSerializer
from confluent_kafka.serialization import StringSerializer

from examples.protobuf.user_pb2 import User

schema = """
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "User",
  "description": "A Confluent Kafka Python User",
  "type": "object",
  "properties": {
    "name": {
      "description": "User's name",
      "type": "string"
    },
    "favorite_number": {
      "description": "User's favorite number",
      "type": "number",
      "exclusiveMinimum": 0
    },
    "favorite_color": {
      "description": "User's favorite color",
      "type": "string"
    },
    "twitter_handle": {
      "description": "User's twitter handle",
      "type": "string"
    },
    "required_field": {
      "description": "Just to demo the issue with required fields",
      "type": "string"
    }
  },
  "required": ["name", "favorite_number", "favorite_color", "twitter_handle"]
}
"""


def user_to_dict(user, ctx):
    return dict(name=user.name,
                favorite_number=user.favorite_number,
                favorite_color=user.favorite_color,
                twitter_handle=user.twitter_handle,
                required_field="required?")


def delivery_report(err, msg):
    if err is not None:
        print(f"Delivery failed for User record {msg.key()}: {err}")
    print(f'User record {msg.key()} successfully produced to {msg.topic()} [{msg.partition}] at offset {msg.offset()}')


def produce_json():
    schema_registry_conf = {'url': 'http://localhost:8081'}
    schema_registry_client = SchemaRegistryClient(schema_registry_conf)
    json_serializer = JSONSerializer(schema, schema_registry_client, user_to_dict)
    p = SerializingProducer({
        'bootstrap.servers': 'localhost:9092',
        'key.serializer': StringSerializer('utf_8'),
        'value.serializer': json_serializer
    })

    user = User(name='Robert Zych',
                favorite_color='blue',
                favorite_number=42,
                twitter_handle='zychr')
    p.produce('user_json', key=str(uuid4()), value=user, on_delivery=delivery_report)
    p.flush()
    print('produced json encoded user')


if __name__ == '__main__':
    produce_json()
