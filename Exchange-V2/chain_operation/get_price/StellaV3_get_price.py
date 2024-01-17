



import requests
import web3

from chain_operation import constants
from chain_operation.exception_handler import chain_exception_catcher

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"

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

    fake_price = (data["sell_pred"] + data["buy_pred"]) / 2
    headers = {
        'User-Agent': UA

    }
    base_url = "https://router-api.stellaswap.com/api/v2/quote/"
    # sell price: exactOut: Amount
    inputToken = token_left_address
    outputToken = token_right_address
    now_amt = int(amount / fake_price * 10 ** token_left_decimals)
    sell_str = f"{inputToken}/{outputToken}/{now_amt}/{my_address}/50"
    req = requests.get(url=base_url + sell_str, headers=headers)
    if req.status_code != 200:
        raise Exception(req.text)
    req_js = req.json()
    sell_route = req_js['result']['execution']
    ret_amt = int(req_js['result']['amountOutOriginal'])

    sell_price = (ret_amt / now_amt) * 10 ** (token_left_decimals - token_right_decimals)

    # buy_price
    inputToken = token_right_address
    outputToken = token_left_address
    now_amt = int(amount * 10 ** token_right_decimals)
    buy_str = f"{inputToken}/{outputToken}/{now_amt}/{my_address}/50"
    req = requests.get(url=base_url + buy_str, headers=headers)
    if req.status_code != 200:
        raise Exception(req.text)
    req_js = req.json()
    buy_route = req_js['result']['execution']
    ret_amt = int(req_js['result']['amountOutOriginal'])

    buy_price = (now_amt / ret_amt) * 10 ** (token_left_decimals - token_right_decimals)
    return {
        "sell_price": sell_price,
        "buy_price": buy_price,
        "route": {
            "sell_route": sell_route,
            "buy_route": buy_route
        }
    }
