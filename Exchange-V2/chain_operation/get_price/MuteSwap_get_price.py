import json
import time

import requests
import web3

from chain_operation.exception_handler import chain_exception_catcher

url = "https://graph2.mute.io/subgraphs/id/QmZfueRArcknULqR9rma72T3KFJ2q32kc6aUnwbZnMZHJ9"


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
    query = "query {" + \
            f"pair(id: \"{exchange_address1.lower()}\") " + \
            """{
        token0 {
          symbol
        }
        token1 {
          symbol
        }
        reserve0
        reserve1
        token0Price
        token1Price
      }
    }
    """

    variables = {}  # 如果有变量，将其添加到此字典中，否则保留为空

    payload = {
        "query": query,
        "variables": variables
    }

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        response_json = response.json()
        token_price = float(response_json["data"]["pair"]["token0Price"])
        sell_price = token_price * (1 - 0.002) / (1 + 0.002)
        buy_price = token_price * (1 + 0.002) / (1 - 0.002)
        ret = {}
        ret["sell_price"] = sell_price
        ret["buy_price"] = buy_price
        return ret
    else:
        print(f"Error: {response.status_code}")
