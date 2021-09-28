import time
from collections import deque

class TransactionQueue:
    def __init__(self, _maxLength):
        self.queue = deque([], maxlen = _maxLength)

    def append(self, _item):
        self.queue.append(_item)
        return

    def isItemInQueue(self, _item):
        if _item in self.queue:
            return True
        else:
            return False

    def arbitrageAlreadyFoundInLastSeconds(self, _arbitrage, _timedelta):
        for arbitrage in self.queue:
            if _arbitrage['pairInAddress'] == arbitrage['pairInAddress'] and (time.time()-arbitrage['timestamp']) < _timedelta:
                return True
        return False


if __name__ == '__main__':
    transactionQueue = TransactionQueue(20)
    for i in range(10):
        arbitrage = {
            'pairAddress': '0x000',
            'amount0Out': 0,
            'amount1Out': 1,
            'timestamp': int(time.time())-10*i
        }
        transactionQueue.append(arbitrage)
    arbitrage = {
        'pairAddress': '0x000',
        'amount0Out': 0,
        'amount1Out': 1,
        'timestamp': int(time.time())
    }
    print(transactionQueue.queue)
    print(transactionQueue.arbitrageAlreadyFoundInLastSeconds(arbitrage, 60))
    time.sleep(2)
    print(transactionQueue.arbitrageAlreadyFoundInLastSeconds(arbitrage, 1))
