import web3
import requests

from chain_operation.constants import chain_list
from chain_operation.exception_handler import chain_exception_catcher


@chain_exception_catcher
def get_price(
        web3: web3.Web3,
        amount: int,
        exchange_address1,
        exchange_address2,
        my_address,
        token_left_address: str,
        token_left_decimals: int,
        token_right_address: str,
        token_right_decimals: int,
        token_slave_address: str,
        token_slave_decimals: int,
        is_multichain: bool,
        chain_id: int,
        data: dict) -> dict:
    # 调用kyberswap的web api获取信息
    url = f"https://aggregator-api.kyberswap.com/{chain_list[str(chain_id)]}/api/v1/routes"
    tokenIn = token_right_address
    tokenOut = token_left_address
    amountIn = int(amount * 10 ** token_right_decimals)
    params = {
        "tokenIn": tokenIn,
        "tokenOut": tokenOut,
        "amountIn": str(amountIn)
    }

    req = requests.get(url=url, params=params)
    res = req.json()
    if res["message"] == "successfully":
        res = res["data"]
        # sell
        buy_price = 1 / ((float(res["routeSummary"]["amountOut"])) / (float(res["routeSummary"]["amountIn"]))) * 10 ** (token_left_decimals - token_right_decimals)
        sell_price = buy_price * (1 - 0.003) / (1 + 0.003)
        ret = {
            "sell_price": sell_price,
            "buy_price": buy_price,
        }
        return ret
    else:
        raise Exception("KyberSwap_get_price.py: get_price() failed.")
