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

    headers = {
        'User-Agent': UA,
        'Origin': 'https://app.uniswap.org',
        'Referer': 'https://app.uniswap.org/',
        'Content-Type': 'application/json',
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',

    }
    base_url = "https://api.uniswap.org/v2/quote"
    # sell price: exactOut: Amount
    sell_query_dict = {

        'sendPortionEnabled': True,
        'configs': [
            {"routingType": "CLASSIC",
             "protocols": ["V2", "V3", "MIXED"],
             "enableUniversalRouter": True,
             "recipient": my_address,
             }
        ],

        'amount': str(int(amount * 10 ** token_right_decimals)),
        'tokenIn': token_left_address,
        'tokenInChainId': chain_id,
        'tokenOut': token_right_address,
        'tokenOutChainId': chain_id,

        'type': 'EXACT_OUTPUT'
    }
    req = requests.post(url=base_url, json=sell_query_dict, headers=headers)
    if req.status_code != 200:
        raise Exception(req.text)
    req_js = req.json()
    sell_route = req_js['quote']
    ret_amt = int(req_js['quote']['amount'])
    ret_quote = int(req_js['quote']['quote'])
    sell_price = (ret_amt / ret_quote) * 10 ** (token_left_decimals - token_right_decimals)

    fake_price = (data['sell_pred'] + data['buy_pred']) / 2
    buy_query_dict = {
        'tokenIn': token_right_address,
        'tokenInChainId': chain_id,
        'tokenOut': token_left_address,
        'tokenOutChainId': chain_id,
        'amount': str(int(amount * 10 ** token_right_decimals)),
        'type': 'EXACT_INPUT',
        'sendPortionEnabled': True,
        'configs': [
            {"routingType": "CLASSIC",
             "protocols": ["V2", "V3", "MIXED"],
             "enableUniversalRouter": True,
             "recipient": my_address,
             }
        ],
    }
    req = requests.post(url=base_url, json=buy_query_dict, headers=headers)
    if req.status_code != 200:
        raise Exception(req.text)
    req_js = req.json()
    ret_amt = int(req_js['quote']['amount'])
    ret_quote = int(req_js['quote']['quote'])
    buy_price = (ret_amt / ret_quote) * 10 ** (token_left_decimals - token_right_decimals)
    buy_route = req_js['quote']
    return {
        "sell_price": sell_price,
        "buy_price": buy_price,
        "route": {
            "sell_route": sell_route,
            "buy_route": buy_route
        }
    }
