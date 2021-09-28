import json

f = open("../research/uniPairs.json")
for line in f:
    uniswapPairs = json.loads(line)
f.close()

f = open("../research/sushiPairs.json")
for line in f:
    sushiswapPairs = json.loads(line)
f.close()



uniswapMatched = []
sushiswapMatched = []
for (uniSupply, uniPair) in uniswapPairs.items():
    if float(uniSupply) < 10000:
        continue
    for (sushiSupply, sushiPair) in sushiswapPairs.items():
        if float(sushiSupply) < 10000:
            continue
        if sushiPair['token0Address'] == uniPair['token0Address'] and sushiPair['token1Address'] in uniPair['token1Address']:
            uniswapMatched.append(uniPair)
            sushiswapMatched.append(sushiPair)
        if sushiPair['token0Address'] == uniPair['token1Address'] and sushiPair['token1Address'] in uniPair['token0Address']:
            uniswapMatched.append(uniPair)
            sushiswapMatched.append(sushiPair)

output = open("../config/uniswapPairsMainnet.json", "w")
pairInfosString = json.dumps(uniswapMatched)
output.write(pairInfosString)

output = open("../config/sushiswapPairsMainnet.json", "w")
pairInfosString = json.dumps(sushiswapMatched)
output.write(pairInfosString)