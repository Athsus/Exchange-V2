
import json
import time

import requests
import web3

from chain_operation.exception_handler import chain_exception_catcher

url = "https://api.pangeaswap.com/graphql"



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

    # 对url=https://api.pangeaswap.com/graphql进行query token
    url = "https://api.pangeaswap.com/graphql"
    query = "query Tokens {\n  tokens {\n    address\n    name\n    symbol\n    decimals\n    isStable\n    isVerified\n    isVisible\n    price\n    reserve\n    volume\n    __typename\n  }\n}"
    payload = {
        "query": query,
        "variables": {}
    }

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    req = requests.post(url=url, json=payload, headers=headers)
    if req.status_code == 200:
        mid_price = None
        for token in req.json()["data"]["tokens"]:
            if token["address"] == token_left_address:
                mid_price = token["price"]
                mid_price = float(mid_price)
                break
        if mid_price is None:
            raise Exception("PangeaSwap get price error： {}, {}, {}".format(req.status_code, req.text, url))
        sell_price = mid_price * (1 - 0.002) / (1 + 0.002)
        buy_price = mid_price * (1 + 0.002) / (1 - 0.002)
        ret = {
            "sell_price": sell_price,
            "buy_price": buy_price
        }
        return ret
    else:
        raise Exception("PangeaSwap get price error： {}, {}, {}".format(req.status_code, req.text, url))

    # 解析出left token的price

    # 分割成买卖价返回成字典
