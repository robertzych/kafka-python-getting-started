from confluent_kafka import DeserializingConsumer
from confluent_kafka.schema_registry.protobuf import ProtobufDeserializer
from confluent_kafka.serialization import StringDeserializer

from protobuf.user_pb2 import User


def consume_protobuf():
    protobuf_deserializer = ProtobufDeserializer(User)
    string_deserializer = StringDeserializer('utf_8')
    # TODO: add link to consumer configs doc
    consumer = DeserializingConsumer({
        'bootstrap.servers': 'localhost:9092',
        'key.deserializer': string_deserializer,
        'value.deserializer': protobuf_deserializer,
        'group.id': 'consumer-group-1',
        'auto.offset.reset': 'earliest'
    })
    consumer.subscribe(['mytopic_protobuf'])

    while True:
        try:
            msg = consumer.poll(1.0)
            if msg is None:
                continue

            user = msg.value()
            if user is not None:
                print(f"User name:{user.name}, "
                      f"favorite number:{user.favorite_number},"
                      f"favorite color:{user.favorite_color},",
                      f"twitter handle:{user.twitter_handle}")
        except KeyboardInterrupt:
            break

    print("closing the consumer")
    consumer.close()


if __name__ == '__main__':
    consume_protobuf()
