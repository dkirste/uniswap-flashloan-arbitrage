#!/usr/bin/python3
from web3 import Web3
from library.producer import KafkaProducer
from library import flashLibrary
import time
import json
import threading
import logging


class EventSubscriber(threading.Thread):
    def __init__(self, _exchange, _pairInfo, _pairABI, _producer, _web3, _logger):
        threading.Thread.__init__(self)
        self.stop_event = threading.Event()

        self.exchange = _exchange
        self.pairInfo = _pairInfo
        self.web3 = _web3
        self.producer = _producer
        self.pair = self.web3.eth.contract(address=self.pairInfo['pairAddress'], abi=_pairABI)
        self.eventFilter = self.pair.events.Sync.createFilter(fromBlock='latest')

        self.logger = _logger

    def stop(self):
        self.stop_event.set()

    def run(self):

        self.eventFilter.get_new_entries()
        while True:
            for syncEvent in self.eventFilter.get_new_entries():
                token0Reserves = syncEvent['args']['reserve0']
                token1Reserves = syncEvent['args']['reserve1']
                blockNumber = syncEvent['blockNumber']
                self.pushReserves(token0Reserves, token1Reserves, blockNumber)
            time.sleep(1)

    def pushReserves(self, _token0Reserves, _token1Reserves, _blockNumber):
        pairUpdate = {
            "pairAddress": self.pairInfo['pairAddress'],
            "token0Symbol": self.pairInfo['token0Symbol'],
            "token0Address": self.pairInfo['token0Address'],
            "token0Reserves": str(_token0Reserves),
            "token0Decimals": self.pairInfo['token0Decimals'],
            "token1Symbol": self.pairInfo['token1Symbol'],
            "token1Address": self.pairInfo['token1Address'],
            "token1Reserves": str(_token1Reserves),
            "token1Decimals": self.pairInfo['token1Decimals'],
            "blockNumber": _blockNumber,
        }
        self.logger.info("Block: {0} Exchange: {1} Update: {2}".format(_blockNumber, self.exchange, pairUpdate))
        self.producer.sendMessage(self.exchange, json.dumps(pairUpdate))
        return


class EventCrawler:
    def __init__(self, _exchange, _kafkaIp, _providerUrl, _pairInfos, _pairABI, _useIPC=False,
                 _loggingLevel=logging.INFO):
        self.exchange = _exchange
        self.kafkaIp = _kafkaIp
        self.providerUrl = _providerUrl
        self.useIPC = _useIPC
        self.pairInfos = _pairInfos
        self.pairABI = _pairABI
        self.logger = flashLibrary.setupLogger("eventCrawler", "./logs/eventCrawler.log", _loggingLevel)

    def start(self):
        if self.useIPC:
            pass
        else:
            web3 = Web3(Web3.HTTPProvider(self.providerUrl))

        producer = KafkaProducer(self.kafkaIp, 3)

        # Set array of subscribers
        subscribers = []

        # Set Pairs
        for pairInfo in self.pairInfos:
            subscribers.append(
                EventSubscriber(_exchange=self.exchange, _pairInfo=pairInfo, _pairABI=self.pairABI, _producer=producer,
                                _web3=web3, _logger=self.logger))
        print("{0} {1} pairs will be listened.".format(len(self.pairInfos), self.exchange))

        # Start all subscribers
        for t in subscribers:
            t.start()
