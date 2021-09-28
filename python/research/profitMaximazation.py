import numpy as np


# USDC - WETH
decimals0 = 6
decimals1 = 18

reserveA0 = 79400913671
reserveA1 = 282985742959986347777
reserveB0 = 19712549347929
reserveB1 = 5073182270164152966140

# UNI - WETH
# decimals0 = 18
# decimals1 = 18
#
# reserveA0 = 230862070917390644
# reserveA1 = 8545054496825366842
#
# reserveB0 = 97419397562703954712
# reserveB1 = 3882289679655075849423


def getAmountOut(_amountIn, _reserveIn, _reserveOut):
    amountInWithFee = _amountIn*997
    numerator = amountInWithFee*_reserveOut
    denominator = (_reserveIn*1000)+amountInWithFee
    amountOut = numerator / denominator
    return amountOut

def getProfit(_amountIn, _decimalsIn, _reserveA0, _reserveA1, _reserveB0, _reserveB1):
    amountIn = _amountIn * (10 ** _decimalsIn)
    amountOut0to1 = getAmountOut(amountIn, _reserveA0, _reserveA1)
    amountOut = getAmountOut(amountOut0to1, _reserveB1, _reserveB0)  # amountOut1to0

    return amountOut - amountIn

def findOptimum(_decimalsIn, _reserveA0, _reserveA1, _reserveB0, _reserveB1):
    upper = 10 ** 6
    lower = 1
    for i in range(20):
        mid = int((upper+lower)/2)
        midupper = int(mid*1.02)
        midlower = int(mid*0.98)

        midupperProfit = getProfit(midupper, _decimalsIn, _reserveA0, _reserveA1, _reserveB0, _reserveB1)
        midlowerProfit = getProfit(midlower, _decimalsIn, _reserveA0, _reserveA1, _reserveB0, _reserveB1)

        if midupperProfit > midlowerProfit:
            lower = mid
        elif midupperProfit < midlowerProfit:
            upper = mid
        elif midupperProfit == midlowerProfit:
            return mid
    if midupperProfit > midlowerProfit:
        return (midupper*(10**_decimalsIn), midupperProfit)
    elif midupperProfit < midlowerProfit:
        return (midlower*(10**_decimalsIn), midlowerProfit)


if __name__ == '__main__':
    #print(findOptimum(decimals0, reserveA0, reserveA1, reserveB0, reserveB1))
    #print(findOptimum(decimals1, reserveB1, reserveB0, reserveA1, reserveA0))
    print(reserveA0/reserveA1)
    print(reserveB0/reserveB1)


