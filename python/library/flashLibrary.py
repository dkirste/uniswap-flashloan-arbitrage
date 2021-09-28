import json
import yaml
import logging
from scipy.optimize import fminbound
from mpmath import mp


def getPairInfosFromJson(_path):
    file = open(_path)
    for line in file:
        return json.loads(line)

def getConfig(_path):
    with open(_path, 'r') as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    return config



def setupLogger(name, log_file, level=logging.INFO):

    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger


def getProfitWithoutDecimals(_amountIn, _reservesA0, _reservesA1, _reservesB0, _reservesB1):
    amountOut0to1 = getAmountOut(_amountIn, _reservesA0, _reservesA1)
    amountOut = getAmountOut(amountOut0to1, _reservesB1, _reservesB0)  # amountOut1to0

    return amountOut - _amountIn

def getProfit(_amountIn, _decimalsIn, _reservesA0, _reservesA1, _reservesB0, _reservesB1):
    amountIn = _amountIn * (10 ** _decimalsIn) # Wei
    amountOut0to1 = getAmountOut(amountIn, _reservesA0, _reservesA1)
    amountOut = getAmountOut(amountOut0to1, _reservesB1, _reservesB0)  # amountOut1to0

    return amountOut - amountIn # Wei level

def profitFunction(x, _reserves0A, _reserves1A, _reserves0B, _reserves1B):
    outputOfFirstSwap = getAmountOut(x, _reserves0A, _reserves1A) # In: 0 Out: 1
    outputOfReswap = getAmountOut(outputOfFirstSwap, _reserves1B, _reserves0B) # In: 1 Out: 0
    return -(outputOfReswap - x)


def findOptimum(_reservesA0, _reservesA1, _reservesB0, _reservesB1):
    mp.dps = 50
    """Returns numbers in 'wei'-form."""
    x = fminbound(profitFunction, x1=-1, x2=10**50, xtol=1, args=(_reservesA0 , _reservesA1, _reservesB0, _reservesB1, ))
    return mp.mpf(str(x))


def calculateRate(_reservesIn, _reservesOut, _tokenInDecimals, _tokenOutDecimals, _amountOfTokens):
    amountIn = (10**_tokenInDecimals) * _amountOfTokens
    amountInWithFee = amountIn * 997
    numerator = amountInWithFee * _reservesOut
    denominator = (_reservesIn * 1000) + amountInWithFee
    amountOut = numerator / denominator

    return amountOut / ((10**_tokenOutDecimals) * _amountOfTokens)


def getAmountOut(_amountIn, _reservesIn, _reservesOut):
    amountInWithFee = _amountIn*997
    numerator = amountInWithFee * _reservesOut
    denominator = (_reservesIn * 1000) + amountInWithFee
    amountOut = numerator / denominator
    return amountOut


def createCurrencyPositions(_pairInfos, WETH):
    CurrencyPositions = {}

    # Setting WETH as 0
    CurrencyPositions[WETH] = 0

    i = 1

    for pair in _pairInfos:
        if not pair['token0Address'] in CurrencyPositions:
            CurrencyPositions[pair['token0Address']] = i
            i += 1
        if not pair['token1Address'] in CurrencyPositions:
            CurrencyPositions[pair['token1Address']] = i
            i += 1
    return CurrencyPositions


def createExchangePositions(_exchanges):
    exchangePosition = {}
    i = 0

    for exchange in _exchanges:
        exchangePosition[exchange] = i
        i += 1

    return exchangePosition


def getSymbolWithNumber(_number, _currencyPositions, _pairInfos):
    pairAddress = getTokenAddressWithNumber(_number, _currencyPositions)
    for pair in _pairInfos:
        if pair['token0Address'] == pairAddress:
            return pair['token0Symbol']
        elif pair['token1Address'] == pairAddress:
            return pair['token1Symbol']
    return "NOT FOUND"


def getTokenAddressWithNumber(_number, _currencyPositions):
    for (tokenAddress, number) in _currencyPositions.items():
        if number == _number:
            return tokenAddress
    print("Number not found!")


def getExchangeWithNumber(_number, _exchangePosition):
    for (exchange, number) in _exchangePosition.items():
        if number == _number:
            return exchange
    print("Number of exchange not found!")


def getDecimals(_token, _pairInfos):
    for pair in _pairInfos:
        if pair['token0Address'] == _token:
            return pair['token0Decimals']
        elif pair['token1Address'] == _token:
            return pair['token1Decimals']
    print("Symbol not found")


def getDecimalsWithNumber(_number, _currencyPositions, _pairInfos):
    token = getTokenAddressWithNumber(_number, _currencyPositions)
    return getDecimals(token, _pairInfos)


def getPairAddress(_exchange, _tokenA, _tokenB, _pairInfos):
    """Returns (pairAddress, AtoB)
    AtoB = True -> token0 = tokenA & token1 = tokenB"""

    for pair in _pairInfos:
        if pair['token0Address'] == _tokenA and pair['token1Address'] == _tokenB:
            return (pair['pairAddress'], True)
        elif pair['token0Address'] == _tokenB and pair['token1Address'] == _tokenA:
            return (pair['pairAddress'], False)
    print("Could not get pair")
    return ('0x000000000000000000', False)

