from web3 import Web3
from web3.contract import Contract

class ArbitrageExecutor:
    def __init__(self, _ownerAddress, _ownerPrivateKey, _httpProvider, _flashloanAddress, _flashloanABI):
        self.ownerAddress = _ownerAddress
        self.ownerPrivateKey = _ownerPrivateKey
        self.web3 = Web3(Web3.HTTPProvider(_httpProvider))
        self.flashloanContract = self.web3.eth.contract(address=_flashloanAddress, abi=_flashloanABI, ContractFactoryClass=Contract)
        self.lastNonce = -1

    def executeArbitrage(self, _pairAddress, _amount0Out, _amount1Out):
        currentNonce = self.web3.eth.getTransactionCount(self.ownerAddress)
        if self.lastNonce == currentNonce:
            currentNonce += 1
        tx = self.flashloanContract.functions.twoCurrencyArbitrage(_pairAddress, _amount0Out ,_amount1Out).buildTransaction \
            ({'from': self.ownerAddress, 'nonce': currentNonce})
        print(tx)
        signed_tx = self.web3.eth.account.signTransaction(tx, private_key=self.ownerPrivateKey)
        #self.web3.eth.sendRawTransaction(signed_tx.rawTransaction)
        lastNonce = currentNonce
        print("Executed arbitrage for: {0}".format(_pairAddress))