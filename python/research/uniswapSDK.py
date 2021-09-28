from uniswap import Uniswap
address = "0x0000000000000000000000000000000000000000"          # or "0x0000000000000000000000000000000000000000", if you're not making transactions
private_key = ""  # or None, if you're not going to make transactions
uniswap_wrapper = Uniswap(address, private_key, version=2)  # pass version=2 to use Uniswap v2
eth = "0x0000000000000000000000000000000000000000"
bat = "0x0D8775F648430679A709E98d2b0Cb6250d2887EF"
dai = "0x89d24A6b4CcB1B6fAA2625fE562bDD9a23260359"
usdc = '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48'

print(uniswap_wrapper.get_eth_token_output_price(dai, 1*10**18))
print(uniswap_wrapper.get_eth_token_input_price(dai, 1*10**18)/uniswap_wrapper.get_eth_token_output_price(dai, 1*10**18))
print(uniswap_wrapper.get_eth_token_input_price(dai, 1*10**18))
print(uniswap_wrapper.get_token_eth_output_price(dai, 1*10**18))
print(uniswap_wrapper.get_token_eth_input_price(dai, 1*10**18))
print(uniswap_wrapper.get_token_eth_output_price(dai, 1*10**18)/uniswap_wrapper.get_token_eth_input_price(dai, 1*10**18))
#print(uniswap_wrapper.get_token_token_input_price(dai, usdc, 10*10**18))
#print(uniswap_wrapper.get_token_token_input_price(dai, usdc, 100*10**18))
#print(uniswap_wrapper.get_eth_token_input_price(dai, 5*10**18))

print(dir(uniswap_wrapper))