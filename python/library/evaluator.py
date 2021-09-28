#!/usr/bin/python3

import threading
import logging
import time
from library import flashLibrary


class Evaluator(threading.Thread):
    def __init__(self, _cube, _quoteGetter, _verifier, _executor, _pairInfos, _exchangePositions, _currencyPositions,
                 _onlyWeth=False,
                 _loggingLevel=logging.INFO):
        self.cube = _cube
        self.quoteGetter = _quoteGetter
        self.verifier = _verifier
        self.executor = _executor

        self.exchangePositions = _exchangePositions
        self.numberOfExchanges = len(self.exchangePositions)
        self.currencyPositions = _currencyPositions
        self.numberOfCurrencies = len(self.currencyPositions)
        self.onlyWeth = _onlyWeth
        self.pairInfos = _pairInfos

        self.logger = flashLibrary.setupLogger("evaluator", "./logs/evaluator.log", _loggingLevel)

        threading.Thread.__init__(self)
        self.stop_event = threading.Event()

    def stop(self):
        self.stop_event.set()

    def run(self):
        while True:
            start_time = time.time()
            self.findTwoCurrencyArbitrage()
            print("Execution took: {}".format(time.time()-start_time))
            time.sleep(5)

    def findTwoCurrencyArbitrage(self):
        for start_exchange in range(self.numberOfExchanges):
            # Only uniswap
            if start_exchange != 0:
                continue

            for m in range(self.numberOfCurrencies):
                # Only evaluate WETH-xxx starting with uniswap
                if m != 0:
                    continue
                for n in range(self.numberOfCurrencies):
                    if self.onlyWeth and m > 0 and n > 0:
                        continue
                    if m == n:
                        continue

                    for e in range(self.numberOfExchanges):
                        if e == start_exchange:
                            continue
                        if self.cube.cube[start_exchange, m, n, 0] < 1 or self.cube.cube[start_exchange, m, n, 1] < 1 or \
                                self.cube.cube[e, n, m, 0] < 1 or self.cube.cube[e, n, m, 1] < 1:
                            continue

                        decimalsIn = flashLibrary.getDecimalsWithNumber(_number=m, _pairInfos=self.pairInfos,
                                                                        _currencyPositions=self.currencyPositions)
                        decimalsSwap = flashLibrary.getDecimalsWithNumber(_number=n, _pairInfos=self.pairInfos,
                                                                          _currencyPositions=self.currencyPositions)
                        tokenIn = flashLibrary.getTokenAddressWithNumber(_number=m,
                                                                         _currencyPositions=self.currencyPositions)
                        swapToken = flashLibrary.getTokenAddressWithNumber(_number=n,
                                                                           _currencyPositions=self.currencyPositions)
                        reservesA0 = self.cube.cube[start_exchange, m, n, 0]
                        reservesA1 = self.cube.cube[start_exchange, m, n, 1]
                        reservesB0 = self.cube.cube[e, n, m, 1]
                        reservesB1 = self.cube.cube[e, n, m, 0]
                        optimizedAmountIn = flashLibrary.findOptimum(_reservesA0=reservesA0,
                                                                     _reservesA1=reservesA1,
                                                                     _reservesB0=reservesB0,
                                                                     _reservesB1=reservesB1)
                        if optimizedAmountIn < 0:
                            continue
                        optimizedProfit = flashLibrary.getProfitWithoutDecimals(_amountIn=optimizedAmountIn,
                                                                                _reservesA0=reservesA0,
                                                                                _reservesA1=reservesA1,
                                                                                _reservesB0=reservesB0,
                                                                                _reservesB1=reservesB1)
                        if optimizedProfit > 0:
                            # self.logger.info(
                            #     "Arbitrage opportunity {0}/{1} - optimizedProfit: {2} optimizedAmountIn: {3} _reservesA0: {4} _reservesA1: {5} _reservesX0: {6} _reservesB1: {7}".format(
                            #         flashLibrary.getSymbolWithNumber(m, self.currencyPositions, self.pairInfos),
                            #         flashLibrary.getSymbolWithNumber(n, self.currencyPositions, self.pairInfos),
                            #         optimizedProfit, optimizedAmountIn, reservesA0, reservesA1, reservesB0, reservesB1
                            #     ))
                            wethProfit = self.verifier.verifyProfitOffchain(_amountIn=optimizedAmountIn,
                                                                            _decimalsIn=decimalsIn, _tokenIn=tokenIn,
                                                                            _reservesA0=reservesA0,
                                                                            _reservesA1=reservesA1,
                                                                            _reservesB0=reservesB0,
                                                                            _reservesB1=reservesB1)
                            # self.logger.info("Arbitrage opportunity at {0}/{1} profit: {2} WETH".format(
                            #     flashLibrary.getSymbolWithNumber(m, self.currencyPositions, self.pairInfos),
                            #     flashLibrary.getSymbolWithNumber(n, self.currencyPositions, self.pairInfos),
                            #     wethProfit))

                            if wethProfit > 0:
                                (pairAddress, _0to1) = flashLibrary.getPairAddress(_exchange=start_exchange,
                                                                                   _tokenA=tokenIn, _tokenB=swapToken,
                                                                                   _pairInfos=self.pairInfos)
                                if _0to1:
                                    amount0Out = 0
                                    amount1Out = flashLibrary.getAmountOut(_amountIn=optimizedAmountIn,
                                                                           _reservesIn=reservesA0,
                                                                           _reservesOut=reservesA1)
                                else:
                                    amount0Out = flashLibrary.getAmountOut(_amountIn=optimizedAmountIn,
                                                                           _reservesIn=reservesA0,
                                                                           _reservesOut=reservesA1)
                                    amount1Out = 0
                                # print("REAL ARBITRAGE at {0}/{1} profit: {2} WETH".format(
                                #     flashLibrary.getSymbolWithNumber(m, self.currencyPositions, self.pairInfos),
                                #     flashLibrary.getSymbolWithNumber(n, self.currencyPositions, self.pairInfos),
                                #     wethProfit))
                                self.logger.info("Profitable arbitrage at {0}/{1} profit: {2} WETH".format(
                                    flashLibrary.getSymbolWithNumber(m, self.currencyPositions, self.pairInfos),
                                    flashLibrary.getSymbolWithNumber(n, self.currencyPositions, self.pairInfos),
                                    wethProfit))
                                try:
                                    infuraProfit = self.verifier.verifyProfitInfura(_tokenIn=tokenIn, _tokenOut=swapToken,
                                                                                _tokenInDecimals=decimalsIn,
                                                                                _tokenOutDecimals=decimalsSwap,
                                                                                _amount0Out=int(amount0Out),
                                                                                _amount1Out=int(amount1Out),
                                                                                _pairInAddress=pairAddress, _0to1=_0to1)
                                    print("infuraProfit:{}".format(infuraProfit))
                                except:
                                    print("Failed to verify profit by infura. Maybe not profitable.")
                                try:
                                    self.executor.executeArbitrage(_pairAddress=pairAddress, _amount0Out=int(amount0Out),
                                                                   _amount1Out=int(amount1Out))
                                except Exception as e:
                                    print("Error while executing arbitrage")
                                    print(e)
