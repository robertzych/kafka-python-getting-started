from confluent_kafka import DeserializingConsumer
from confluent_kafka.schema_registry.json_schema import JSONDeserializer
from confluent_kafka.serialization import StringDeserializer

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
    }
  },
  "required": ["name", "favorite_number", "favorite_color", "twitter_handle"]
}
"""


def dict_to_user(obj, ctx):
    if obj is None:
        return None

    return User(name=obj['name'],
                favorite_number=obj['favorite_number'],
                favorite_color=obj['favorite_color'],
                twitter_handle=obj['twitter_handle'])


def consume_json():
    json_deserializer = JSONDeserializer(schema, from_dict=dict_to_user)
    string_deserializer = StringDeserializer('utf_8')
    # https://docs.confluent.io/platform/current/installation/configuration/consumer-configs.html
    consumer = DeserializingConsumer({
        'bootstrap.servers': 'localhost:9092',
        'key.deserializer': string_deserializer,
        'value.deserializer': json_deserializer,
        'group.id': 'json-consumer-group-1',
        'auto.offset.reset': 'earliest'
    })
    consumer.subscribe(['user_json'])

    while True:
        try:
            msg = consumer.poll(1.0)
            if msg is None:
                continue

            user = msg.value()
            if user is not None:
                print(f'User name: {user.name}, '
                      f'favorite number:{user.favorite_number}, '
                      f'favorite color:{user.favorite_color}, '
                      f'twitter handle:{user.twitter_handle}')
        except KeyboardInterrupt:
            break

    print('closing the consumer')
    consumer.close()


if __name__ == '__main__':
    consume_json()
