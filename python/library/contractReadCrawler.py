#!/usr/bin/python3
from web3 import Web3
import logging
from library.producer import KafkaProducer
from library import flashLibrary
import json


class InfuraCrawler:
    def __init__(self, _exchange, _pairInfos, _pairABI, _kafkaIp, _providerUrl, _loggingLevel=logging.INFO):
        self.exchange = _exchange
        self.pairInfos = _pairInfos
        self.pairABI = _pairABI
        self.producer = KafkaProducer(_kafkaIp, 3)
        self.web3 = Web3(Web3.HTTPProvider(_providerUrl))

        self.logger = flashLibrary.setupLogger("infuraCrawler", "./logs/infuraCrawler.log", _loggingLevel)

    def start(self):
        for pairInfo in self.pairInfos:
            pairAddress = pairInfo['pairAddress']
            (token0Reserves, token1Reserves, timestamp) = self.getReserves(pairAddress)
            self.pushReserves(self.exchange, pairInfo, token0Reserves, token1Reserves, timestamp)
        print("crawled {0} {1} pairs.".format(len(self.pairInfos), self.exchange))
        self.producer.flushMessages()

    def getReserves(self, _pairAddress):
        pair = self.web3.eth.contract(address=_pairAddress, abi=self.pairABI)
        blockNumberReturn = self.web3.eth.get_block('latest')
        blockNumber = blockNumberReturn['number']
        (token0Reserves, token1Reserves, timestamp) = pair.functions.getReserves().call()

        return (token0Reserves, token1Reserves, blockNumber)

    def pushReserves(self, _exchange, _pairInfo, _token0Reserves, _token1Reserves, _blockNumber):
        pairUpdate = {
            "pairAddress": _pairInfo['pairAddress'],
            "token0Symbol": _pairInfo['token0Symbol'],
            "token0Address": _pairInfo['token0Address'],
            "token0Reserves": str(_token0Reserves),
            "token0Decimals": _pairInfo['token0Decimals'],
            "token1Symbol": _pairInfo['token1Symbol'],
            "token1Address": _pairInfo['token1Address'],
            "token1Reserves": str(_token1Reserves),
            "token1Decimals": _pairInfo['token1Decimals'],
            "blockNumber": _blockNumber,
        }
        self.logger.info("Block: {0} Exchange: {1} Update: {2}".format(_blockNumber, _exchange, pairUpdate))
        self.producer.sendMessage(_exchange, json.dumps(pairUpdate))
