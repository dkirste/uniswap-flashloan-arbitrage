from confluent_kafka import Producer
import socket

class KafkaProducer:
    def __init__(self, _ipAddress, _autoFlush= 100):
        self.producer = Producer({'bootstrap.servers': "{0}:9092".format(_ipAddress), 'client.id': socket.gethostname()})
        self.autoFlush = _autoFlush
        self.messageCount = 0

    def sendMessage(self, _topic, _message):
        self.messageCount += 1
        self.producer.produce(_topic, key='json', value=_message)

        if self.messageCount % self.autoFlush == 0:
            self.producer.flush()

    def flushMessages(self):
        self.producer.flush()



