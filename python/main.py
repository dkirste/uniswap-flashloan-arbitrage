#!/usr/bin/python3
from library import flashLibrary, eventCrawler, contractReadCrawler, quoteGetter, cube, arbitrageExecutor, \
    arbitrageProfitVerifier, evaluator
from mpmath import mp
import time

mp.dps = 50

config = flashLibrary.getConfig("config/basic.yml")
secretConfig = flashLibrary.getConfig("config/secret.yml")
exchanges = ['uniswap', 'sushiswap']
uniPairInfos = flashLibrary.getPairInfosFromJson("config/uniswapPairsMainnet.json")
sushiPairInfos = flashLibrary.getPairInfosFromJson("config/sushiswapPairsMainnet.json")

exchangePositions = flashLibrary.createExchangePositions(exchanges)
currencyPositions = flashLibrary.createCurrencyPositions(_pairInfos=uniPairInfos, WETH=config['weth'])

uniInitialCrawler = contractReadCrawler.InfuraCrawler(_exchange='uniswap', _pairABI=config['pairABI'],
                                                      _pairInfos=uniPairInfos, _kafkaIp=config['kafkaIp'],
                                                      _providerUrl=config['infuraUrl'])
uniInitialCrawler.start()

sushiInitialCrawler = contractReadCrawler.InfuraCrawler(_exchange='sushiswap', _pairABI=config['pairABI'],
                                                        _pairInfos=sushiPairInfos, _kafkaIp=config['kafkaIp'],
                                                        _providerUrl=config['infuraUrl'])
sushiInitialCrawler.start()

uniEventCrawler = eventCrawler.EventCrawler(_exchange='uniswap',
                                            _kafkaIp=config['kafkaIp'], _providerUrl=config['gethUrl'],
                                            _pairInfos=uniPairInfos, _pairABI=config['pairABI'], _useIPC=False)
uniEventCrawler.start()

sushiEventCrawler = eventCrawler.EventCrawler(_exchange='sushiswap',
                                              _kafkaIp=config['kafkaIp'], _providerUrl=config['gethUrl'],
                                              _pairInfos=sushiPairInfos, _pairABI=config['pairABI'], _useIPC=False)
sushiEventCrawler.start()

quoteGetter = quoteGetter.QuoteGetter(_referenceCurrency=config['weth'],
                                      _referenceCurrencyDecimals=config['wethDecimals'],
                                      _pairInfos=uniPairInfos, _network=config['network'])
quoteGetter.start()

arbitrageVerifier = arbitrageProfitVerifier.ArbitrageProfitVerifier(_quoteGetter=quoteGetter,
                                                                    _httpProvider=config['infuraUrl'],
                                                                    _uniRouterAddress=config['uniRouterAddress'],
                                                                    _sushiRouterAddress=config['sushiRouterAddress'],
                                                                    _routerABI=config['routerABI'],
                                                                    _senderAddress=secretConfig['ownerAddress'],
                                                                    _flashloanAddress=config['flashloanAddress'],
                                                                    _flashloanABI=config['flashloanABI'])
arbitrageVerifier.start()

arbitrageExecutor = arbitrageExecutor.ArbitrageExecutor(_ownerAddress=secretConfig['ownerAddress'],
                                                        _ownerPrivateKey=secretConfig['ownerPrivateKey'],
                                                        _flashloanAddress=config['flashloanAddress'],
                                                        _flashloanABI=config['flashloanABI'],
                                                        _httpProvider=config['infuraUrl'])

cube = cube.Cube(_kafkaIP=config['kafkaIp'], _consumerGroup="cube-{}".format(int(time.time())), _topics=exchanges,
                 _exchangePositions=exchangePositions, _currencyPositions=currencyPositions)
cube.start()

evaluator = evaluator.Evaluator(_cube=cube, _quoteGetter=quoteGetter, _verifier=arbitrageVerifier,
                                _executor=arbitrageExecutor, _pairInfos=uniPairInfos,
                                _exchangePositions=exchangePositions,
                                _currencyPositions=currencyPositions, _onlyWeth=True)
evaluator.start()
