import numpy as np

currencies = ['USDT', 'BNB', 'USDC', 'UNI', 'LINK']
exchanges = ['UNIS', 'SUSHI', 'CRO']

def fill_cube_no_arbitrage():
    for e in range(len(exchanges)):
        for m in range(len(currencies)):
            for n in range(len(currencies)):
                cube[e,m,n] = price[n] / price[m]

def fill_cube_all_arbitrage():
    for e in range(len(exchanges)):
        for m in range(len(currencies)):
            for n in range(len(currencies)):
                if price[m] / price[n] > 1:
                    cube[e,m,n] = price[n] / price[m] + 1*(e+1)
                #elif price[m] / price[n] < 1:
                #    cube[e,m,n] = price[n] / price[m] - 0.1
                else:
                    cube[e,m,n] = price[n] / price[m]

def fill_cube_one_arbitrage():
    for e in range(len(exchanges)):
        for m in range(len(currencies)):
            for n in range(len(currencies)):
                # Arbitrage for USDT-BNB on UNI
                if e == 0 and m == 0 and n == 1:
                    # Pay 235 USDT instead of 225 USDT for 1 BNB
                    cube[e,m,n] = (price[n]+10) / price[m]
                elif e == 0 and m == 1 and n == 0:
                    # Also pay less BNB for 1 USDT
                    cube[e,m,n] = price[n] / (price[m] + 10)
                else:
                    cube[e,m,n] = price[n] / price[m]

def find_two_currencies_arbitrage():
    execs = 0
    for start_e in range(len(exchanges)):
        #if start_e != 0:
        #    continue
        for m in range(len(currencies)):
            for n in range(len(currencies)):
                for e in range(len(exchanges)):
                    #if cube[start_e,m,n] - 1/cube[e,n,m] != 0:
                    #    print("Inequality at {0}-{1} with expected return of x{2}".format(currencies[m], currencies[n], cube[start_e,m,n] - 1/cube[e,n,m]))
                    #    print("e: {0}   m: {1}   n: {2}".format(e, m, n))
                    ineq = cube[start_e,m,n] - 1/cube[e,n,m]
                    arbitrage_profit = cube[start_e,m,n] / (1/cube[e,n,m])
                    if arbitrage_profit > 1.01:
                        print("Found arbitrage at {0}-{1} with expected return of x{2}. Start: {3}, End: {4}".format(currencies[m], currencies[n], ineq, exchanges[start_e], exchanges[e]))
                        print((arbitrage_profit))



if __name__ == '__main__':
    cube = np.zeros((len(exchanges), len(currencies), len(currencies)))

    price = [1, 190, 1, 22, 25]
    fill_cube_one_arbitrage()

    find_two_currencies_arbitrage()