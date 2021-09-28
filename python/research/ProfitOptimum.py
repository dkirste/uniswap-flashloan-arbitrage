import numpy as np
from scipy.optimize import fminbound, newton
from mpmath import mp

def profitFunction(x, _reserves0A, _reserves1A, _reserves0B, _reserves1B):
    outputOfFirstSwap = getAmountOut(x, _reserves0A, _reserves1A) # In: 0 Out: 1
    outputOfReswap = getAmountOut(outputOfFirstSwap, _reserves1B, _reserves0B) # In: 1 Out: 0
    return -(outputOfReswap - x)

def getAmountOut(_amountIn, _reservesIn, _reservesOut):
    amountInWithFee = _amountIn*997
    numerator = amountInWithFee * _reservesOut
    denominator = (_reservesIn * 1000) + amountInWithFee
    amountOut = numerator / denominator
    return amountOut

def findOptimum(_decimalsIn, _reservesA0, _reservesA1, _reservesB0, _reservesB1):
    """Returns numbers in 'wei'-form."""
    upper = 10 ** 3
    lower = 1
    for i in range(20):

        mid = (upper+lower)/2
        midupper = mid*1.02
        midlower = mid*0.98

        midupperProfit = getProfit(midupper, _decimalsIn, _reservesA0, _reservesA1, _reservesB0, _reservesB1)
        midlowerProfit = getProfit(midlower, _decimalsIn, _reservesA0, _reservesA1, _reservesB0, _reservesB1)

        if midupperProfit > midlowerProfit:
            lower = mid
        elif midupperProfit < midlowerProfit:
            upper = mid
        elif midupperProfit == midlowerProfit:
            return mid
    if midupperProfit > midlowerProfit:
        return (midupper * (10 ** _decimalsIn), int(midupperProfit))
    elif midupperProfit < midlowerProfit:
        return (midlower * (10 ** _decimalsIn), int(midlowerProfit))


def getProfit(_amountIn, _decimalsIn, _reservesA0, _reservesA1, _reservesB0, _reservesB1):
    amountIn = _amountIn * (10 ** _decimalsIn)
    amountOut0to1 = getAmountOut(amountIn, _reservesA0, _reservesA1)
    amountOut = getAmountOut(amountOut0to1, _reservesB1, _reservesB0)  # amountOut1to0

    return amountOut - amountIn

def derivative(x, a, b, c, d):
    #return -((997000 * a * b * (1000000000 * a**2 * c * (1000*c + 997*d) + 1994000000*a*c*x*(997*b + 1000*c + 997*d) + 994009*x**2 * (994009*b**2 + 1994000*b*c + 1000*c * (1000*c + 997*d)))) / ((1000*a + 997*x)**2*(1000000*a*c + 997*x*(997*b+1000*c))**2))
    return -((997000 * a * b * (1000000000 * a**2 * c * (1000*c - 997*d) + 1994000000*a*c*x*(997*b + 1000*c - 997*d) + 994009*x**2 * (994009*b**2 + 1994000*b*c + 1000*c * (1000*c - 997*d)))) / ((1000*a + 997*x)**2*(1000000*a*c + 997*x*(997*b+1000*c))**2))


# #print(profitFunction(890, _reserves0A=1000, _reserves1A=1000, _reserves0B=10000, _reserves1B=1000))
# for i in range(1):
#     x0 = 1800
#     x = fminbound(profitFunction, x1=-1, x2=10**36, xtol=1, args=(mp.mpf("1e+25"), mp.mpf("1e+25"), mp.mpf("1e+25"), mp.mpf("1e+25"), ))
#     print(int(x))
#
#
# #x = fminbound(profitFunction, x1=-1, x2=2.8537725127970615e+22, xtol=1, args=(int(4.8537725127970615e+22), int(149442615312384.0), int(7.220229019035572e+22), int(221933207552000.0), ))
x = fminbound(profitFunction, x1=-1, x2=10**50, xtol=1, full_output=True, args=(1000, 1000, 1100, 1000, ))
# print(x)


for i in range(50):
    if i<18:
        continue
    x = fminbound(profitFunction, x1=-1, x2=10 ** 50, xtol=1, full_output=True, args=(10**i, 10**(i-12), 10**i-10**(i-1), 10**(i-12),))
    print(x)
    #print(newton(derivative, x0=10**(i-3), rtol=1, tol=1, args=(10**(i-12),10**i,10**(i-12),10**i + 10**(i-1),)))
