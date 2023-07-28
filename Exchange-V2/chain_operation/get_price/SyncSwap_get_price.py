import requests
import web3

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

    chain_name = chain_list[str(chain_id)]
    url = f"https://api.dexscreener.com/latest/dex/pairs/{chain_name}/{exchange_address1}"
    req = requests.get(url=url)
    res = req.json()
    price_native = float(res['pairs'][0]['priceNative'])
    price_sell = price_native * (1 - 0.002) / (1 + 0.002)
    price_buy = price_native * (1 + 0.002) / (1 - 0.002)
    ret = {}
    ret["sell_price"] = price_sell
    ret["buy_price"] = price_buy
    return ret