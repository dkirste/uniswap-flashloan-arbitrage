const Flashloan = artifacts.require("Flashloan");

module.exports = function (deployer) {
  const uniswapFactory = '0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f'; //MAINNET
  const sushiswapFactory = '0xC0AEe478e3658e2610c5F7A4A2E1777cE9e4f2Ac'; //MAINNET
  const uniswapRouter = '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D'; //MAINNET
  const sushiswapRouter = '0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F'; //MAINNET

  //const uniswapFactory = '0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f'; //ROPSTEN
  //const sushiswapRouter = '0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506'; //ROPSTEN

  deployer.deploy(Flashloan, uniswapFactory, sushiswapRouter);
};
