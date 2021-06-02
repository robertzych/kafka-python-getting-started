from uuid import uuid4

from confluent_kafka import SerializingProducer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.protobuf import ProtobufSerializer
from confluent_kafka.serialization import StringSerializer

from examples.protobuf.user_pb2 import User


def produce_protobuf():
    schema_registry_conf = {'url': 'http://localhost:8081'}
    schema_registry_client = SchemaRegistryClient(schema_registry_conf)
    protobuf_serializer = ProtobufSerializer(User, schema_registry_client)
    # https://docs.confluent.io/platform/current/installation/configuration/producer-configs.html
    p = SerializingProducer({
        'bootstrap.servers': 'localhost:9092',
        'key.serializer': StringSerializer('utf_8'),
        'value.serializer': protobuf_serializer
    })
    user = User(name='Robert Zych',
                favorite_color='blue',
                favorite_number=42,
                twitter_handle='zychr')
    p.produce('mytopic_protobuf', key=str(uuid4()), value=user)
    p.flush()
    print('produced protobuf encoded user')


if __name__ == '__main__':
    produce_protobuf()
