pragma solidity >=0.6.6;

import "./UniswapV2Library.sol";
import "./interfaces/IUniswapV2Router02.sol";
import "./interfaces/IUniswapV2Pair.sol";
import "./interfaces/IUniswapV2Factory.sol";
import "./interfaces/IERC20.sol";
import "@openzeppelin/contracts/math/SafeMath.sol";

contract flashloan {
    using SafeMath for uint256;
    address public factory;
    uint256 public deadline = 1 hours;
    IUniswapV2Router02 public sushiRouter;

    constructor(address _factory, address _sushiRouter) public {
        factory = _factory;
        sushiRouter = IUniswapV2Router02(_sushiRouter);
    }

    function twoCurrencyArbitrage(
        address _pairIn,
        uint256 _amount0Out,
        uint256 _amount1Out
    ) external {
        require(_amount0Out == 0 || _amount1Out == 0, "Flash: WRONG AMOUNTS");
        IUniswapV2Pair(_pairIn).swap(
            _amount0Out,
            _amount1Out,
            address(this),
            bytes("not empty")
        );
    }

    function uniswapV2Call(
        address _sender, // my flashloan contract
        uint256 _amount0,
        uint256 _amount1,
        bytes calldata _data
    ) external {
        address token0 = IUniswapV2Pair(msg.sender).token0(); // token0 of uniswap
        address token1 = IUniswapV2Pair(msg.sender).token1(); // token1 of uniswap

        uint256 amountInToken = _amount0 == 0 ? _amount1 : _amount0;

        address[] memory path = new address[](2);
        address[] memory originalpath = new address[](2);
        path[0] = _amount0 == 0 ? token1 : token0;
        path[1] = _amount0 == 0 ? token0 : token1;
        originalpath[0] = path[1];
        originalpath[1] = path[0];

        require(
            msg.sender == UniswapV2Library.pairFor(factory, token0, token1),
            "Unauthorized"
        );

        IERC20 token = IERC20(path[0]);

        token.approve(address(sushiRouter), amountInToken);

        uint256 amountRequired =
            UniswapV2Library.getAmountsIn(factory, amountInToken, originalpath)[0];
        uint256 amountReceived =
            sushiRouter.swapExactTokensForTokens(
                amountInToken,
                amountRequired,
                path,
                address(this),
                block.timestamp + deadline
            )[1];

        IERC20 otherToken = IERC20(_amount0 == 0 ? token0 : token1);
        otherToken.transfer(msg.sender, amountRequired);
        otherToken.transfer(tx.origin, amountReceived - amountRequired);
    }
}
