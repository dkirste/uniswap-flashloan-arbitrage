import requests
import threading
import time
from library import flashLibrary
import logging


class QuoteGetter(threading.Thread):
    def __init__(self, _referenceCurrency, _referenceCurrencyDecimals, _pairInfos, _network,
                 _loggingLevel=logging.INFO):
        self.referenceCurrency = _referenceCurrency
        self.referenceCurrencyDecimals = int(_referenceCurrencyDecimals)
        self.pairInfos = _pairInfos
        self.network = _network

        self.currencies = self.createCurrencies()
        self.logger = flashLibrary.setupLogger("quoteGetter", "./logs/quoteGetter.log", _loggingLevel)

        threading.Thread.__init__(self)
        self.stop_event = threading.Event()

    def stop(self):
        self.stop_event.set()

    def run(self):
        if self.network == 'Ropsten':
            for (tokenAddress, quote) in self.currencies.items():
                self.currencies[tokenAddress] = 1
            while True:
                time.sleep(60)

        for (tokenAddress, quote) in self.currencies.items():
            self.currencies[tokenAddress] = self.getQuote1inch(tokenAddress,
                                                               flashLibrary.getDecimals(_token=tokenAddress,
                                                                                        _pairInfos=self.pairInfos))
        while True:
            for (tokenAddress, quote) in self.currencies.items():
                self.currencies[tokenAddress] = self.getQuote1inch(tokenAddress,
                                                                   flashLibrary.getDecimals(_token=tokenAddress,
                                                                                            _pairInfos=self.pairInfos))
                self.logger.info("Updated {0} with quote of {1}".format(tokenAddress, self.currencies[tokenAddress]))
            time.sleep(10)  # Wait 10sec to refresh

    def createCurrencies(self):
        currencies = {}

        for pair in self.pairInfos:
            if not pair['token0Address'] in currencies:
                currencies[pair['token0Address']] = float(0)
            if not pair['token1Address'] in currencies:
                currencies[pair['token1Address']] = float(0)
        return currencies

    def getData1inch(self, _address, _decimals):
        if _address == self.referenceCurrency:
            return {'toTokenAmount': 10 ** _decimals}
        response = requests.get(
            'https://api.1inch.exchange/v3.0/1/quote?fromTokenAddress={0}&toTokenAddress={1}&amount={2}'.format(
                _address, self.referenceCurrency, 1 * (10 ** _decimals)))
        return response.json()

    def getQuote1inch(self, _address, _decimals):
        for i in range(5):
            try:
                data = self.getData1inch(_address, _decimals)
                fullTokenQuote = float(data['toTokenAmount']) / (
                        10 ** self.referenceCurrencyDecimals)  # Quote of 1inch is in amount of dai
                return fullTokenQuote
            except:
                # Sleep to compress network outage
                time.sleep(0.2)
                continue
        # Return the current currency, since the script is not able to determine the new quote
        return self.currencies[_address]
        print("Failed at {0}".format(_address))

    def getWethQuote(self, _tokenAddress):
        try:
            return self.currencies[_tokenAddress]
        except:
            print("Quote for {0} not found".format(_tokenAddress))
            return 0
