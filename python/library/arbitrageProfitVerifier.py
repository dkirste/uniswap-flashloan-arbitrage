import threading
from web3 import Web3
import logging
import requests
from web3.contract import Contract


from library import flashLibrary


class ArbitrageProfitVerifier(threading.Thread):
    def __init__(self, _quoteGetter, _httpProvider, _uniRouterAddress, _sushiRouterAddress, _flashloanAddress, _flashloanABI, _routerABI, _senderAddress,
                 _estimatedGasForContractExecution=210000,
                 _loggingLevel=logging.INFO):
        self.quoteGetter = _quoteGetter
        self.web3 = Web3(Web3.HTTPProvider(_httpProvider))
        self.gasPrice = 1
        self.estimatedGasForContractExecution = _estimatedGasForContractExecution
        self.uniRouter = self.web3.eth.contract(address=_uniRouterAddress, abi=_routerABI)
        self.sushiRouter = self.web3.eth.contract(address=_sushiRouterAddress, abi=_routerABI)
        self.flashloanContract = self.web3.eth.contract(address=_flashloanAddress, abi=_flashloanABI, ContractFactoryClass=Contract)
        self.senderAddress = _senderAddress

        self.logger = flashLibrary.setupLogger("arbitrageProfitVerifier", "./logs/arbitrageProfitVerifier.log", _loggingLevel)

        threading.Thread.__init__(self)
        self.stop_event = threading.Event()

    def verifyProfitInfura(self, _tokenIn, _tokenOut, _tokenInDecimals, _tokenOutDecimals, _pairInAddress, _amount0Out,
                           _amount1Out, _0to1):
        if _0to1:
            amountIn = self.uniRouter.functions.getAmountsIn(_amount1Out, [_tokenIn, _tokenOut]).call()[0]
            amountOut = self.sushiRouter.functions.getAmountsOut(_amount1Out, [_tokenOut, _tokenIn]).call()[1]
        else:
            amountIn = self.uniRouter.functions.getAmountsIn(_amount0Out, [_tokenIn, _tokenOut]).call()[0]
            amountOut = self.sushiRouter.functions.getAmountsOut(_amount0Out, [_tokenOut, _tokenIn]).call()[1]

        tokenOuote = self.quoteGetter.getWethQuote(_tokenIn)
        amountOutWeth = (int(amountOut) - int(amountIn))

        gasCosts = self.estimateGas(_pairInAddress=_pairInAddress, _amount0Out=_amount0Out, _amount1Out=_amount1Out)

        profit = amountOutWeth - (gasCosts * (10 ** 9))
        self.logger.info("amountIn: {0} amountOut: {1} amountOut: {1} tokenQuote: {2} amountOutWeth: {3} profit: {4} gasCost: {5}".format(
            amountIn, amountOut, tokenOuote, amountOutWeth, profit, gasCosts))
        return profit

    def verifyProfitOffchain(self, _amountIn, _decimalsIn, _tokenIn, _reservesA0, _reservesA1, _reservesB0,
                             _reservesB1):
        tokenInProfit = flashLibrary.getProfitWithoutDecimals(_amountIn=_amountIn, _reservesA0=_reservesA0,
                                               _reservesA1=_reservesA1, _reservesB0=_reservesB0,
                                               _reservesB1=_reservesB1) #Wei

        #amountOutWeth = tokenInProfit / (10 ** _decimalsIn) * self.quoteGetter.getWethQuote(_tokenIn)
        # No multiplication needed since WETH is in and out
        amountOutWeth = tokenInProfit / (10 ** _decimalsIn) # Wei to eth

        gasCosts = self.estimatedGasForContractExecution * self.gasPrice
        profit = amountOutWeth - (gasCosts / (10 ** 9)) # Gas in gwei to eth

        return profit

    def estimateGas(self, _pairInAddress, _amount0Out, _amount1Out):
        gasCost = self.flashloanContract.functions.twoCurrencyArbitrage(_pairInAddress, _amount0Out,_amount1Out).estimateGas({'from': self.senderAddress})*(self.gasPrice*1.5)
        #gasCost = 210000 * (self.gasPrice * 1.5)
        print(gasCost)
        return gasCost

    def stop(self):
        self.stop_event.set()

    def run(self):
        while True:
            try:
                response = requests.get('https://ethgasstation.info/api/ethgasAPI.json?').json()
                self.gasPrice = int(response['fastest']) / 10
            except:
                pass
