#!/usr/bin/python3
from confluent_kafka import Consumer


class KafkaConsumer:
    def __init__(self, _ipAddress):
        self.consumer = Consumer({'bootstrap.servers': "{0}:9092".format(_ipAddress), 'group.id': "confluent_kafka", 'auto.offset.reset': 'smallest'})

    def consume(self,_topics):
        """ Function takes a pointer to a function!!!"""
        self.consumer.subscribe(_topics)

        while True:
            msg = self.consumer.poll(1.0)

            if msg is None:
                continue
            if msg.error():
                print("Consumer error: {}".format(msg.error()))
                continue

            print(msg.topic() + " - " + msg.value().decode('utf-8'))

if __name__ == '__main__':
    consumer = KafkaConsumer('192.168.0.216')
    consumer.consume(['uniswap', 'sushiswap'])

