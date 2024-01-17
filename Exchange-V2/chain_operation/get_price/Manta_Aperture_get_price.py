import requests
import web3

from chain_operation import constants
from chain_operation.exception_handler import chain_exception_catcher

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Origin": "https://aperture.finance/",
    "Referer": "https://aperture.finance/",
    "authority": "manta-routing.aperture.finance",

}

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
    base_url = "https://manta-routing.aperture.finance/quote"
    # sell price: exactOut: Amount
    sell_query_dict = {
        'tokenInAddress': token_left_address,
        'tokenInChainId': chain_id,
        'tokenOutAddress': token_right_address,
        'tokenOutChainId': chain_id,
        'amount': int(amount * 10 ** token_right_decimals),
        'type': 'exactOut',
        'configs': [
            {"routingType": "CLASSIC", "protocols": ["V2", "V3", "MIXED"]}
        ]
    }
    tail = []
    for key, val in sell_query_dict.items():
        tail.append(f'{key}={val}')
    tail = '&'.join(tail)
    req = requests.get(url=base_url + '?' + tail, headers=headers)
    if req.status_code != 200:
        raise Exception(req.text)
    sell_req_js = req.json()
    ret_amt = int(sell_req_js['amount'])
    ret_quote = int(sell_req_js['quote'])
    sell_price = (ret_amt / ret_quote) * 10 ** (token_left_decimals - token_right_decimals)

    fake_price = (data['sell_pred'] + data['buy_pred']) / 2
    buy_query_dict = {
        'tokenInAddress': token_right_address,
        'tokenInChainId': chain_id,
        'tokenOutAddress': token_left_address,
        'tokenOutChainId': chain_id,
        'amount': int(amount * 10 ** token_right_decimals),  # int((amount / fake_price) * 10 ** token_left_decimals),
        'type': 'exactIn'
    }
    tail = []
    for key, val in buy_query_dict.items():
        tail.append(f'{key}={val}')
    tail = '&'.join(tail)
    req = requests.get(url=base_url + '?' + tail, headers=headers)
    if req.status_code != 200:
        raise Exception(req.text)
    buy_req_js = req.json()
    ret_amt = int(buy_req_js['amount'])
    ret_quote = int(buy_req_js['quote'])
    buy_price = (ret_amt / ret_quote) * 10 ** (token_left_decimals - token_right_decimals)

    return {
        "sell_price": sell_price,
        "buy_price": buy_price,
        "route": {
            "sell_route": sell_req_js["route"],
            "buy_route": buy_req_js["route"]
        }
    }
