from confluent_kafka import Producer


def produce_hello_world():
    p = Producer({'bootstrap.servers': 'localhost:9092'})
    p.produce('mytopic', key='hello', value='world')
    p.flush(30)


if __name__ == '__main__':
    produce_hello_world()
