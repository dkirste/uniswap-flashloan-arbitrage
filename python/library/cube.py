import threading
from confluent_kafka import Consumer
import json
from mpmath import mp, matrix


class Cube(threading.Thread):
    def __init__(self, _kafkaIP, _consumerGroup, _topics, _exchangePositions, _currencyPositions):
        self.topics = _topics
        self.consumer = Consumer({'bootstrap.servers': "{0}:9092".format(_kafkaIP), 'group.id': _consumerGroup,
                                  'auto.offset.reset': 'smallest'})
        self.exchangePositions = _exchangePositions
        self.currencyPositions = _currencyPositions
        self.cube = matrix(len(_exchangePositions), len(_currencyPositions), len(_currencyPositions), 2)


        threading.Thread.__init__(self)
        self.stop_event = threading.Event()

    def stop(self):
        self.stop_event.set()

    def run(self):
        self.consumer.subscribe(self.topics)

        while not self.stop_event.is_set():
            msg = self.consumer.poll(1.0)

            if msg is None:
                continue
            elif msg.error():
                print("Consumer error: {}".format(msg.error()))
                continue
            else:
                # print("Received message from: " + msg.topic())
                # print('.', end='')
                self.updateCube(msg.topic(), json.loads(msg.value().decode('utf-8')))

        self.consumer.close()

    def updateCube(self, _exchange, _pairUpdate):
        e = self.exchangePositions[_exchange]
        m = self.currencyPositions[_pairUpdate['token0Address']]
        n = self.currencyPositions[_pairUpdate['token1Address']]
        self.cube[e, m, n, 0] = mp.mpf(_pairUpdate['token0Reserves'])
        self.cube[e, m, n, 1] = mp.mpf(_pairUpdate['token1Reserves'])
        self.cube[e, n, m, 0] = mp.mpf(_pairUpdate['token1Reserves'])
        self.cube[e, n, m, 1] = mp.mpf(_pairUpdate['token0Reserves'])
