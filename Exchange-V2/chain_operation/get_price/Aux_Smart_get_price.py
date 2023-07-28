import json
import os
import subprocess
import time

import requests
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
import web3 as web3

headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; \
        Win64; x64) AppleWthibebKit/537.36 (KHTML, lik\
        e Gecko) Chrome/89.0.4389.90 Safari/537.36 Edg/\
        89.0.774.54'
    }

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
    while True:
        try:
            ret = {}
            fake_price = (data["sell_pred"] + data["buy_pred"]) / 2
            amount = amount / fake_price
            # === get sell price ===
            json_data = {
                "operationName": "PoolPriceIn",
                "query": "query PoolPriceIn($poolInput: PoolInput!, $coinTypeIn: String!, $coinTypeOut: String!, $amount: Float!, $slippagePct: Float!) {\n  pool(poolInput: $poolInput) {\n    quoteExactIn(\n      coinTypeOut: $coinTypeOut\n      coinTypeIn: $coinTypeIn\n      amountIn: $amount\n      slippagePct: $slippagePct\n    ) {\n      expectedAmountOut\n      minAmountOut\n      feeAmount\n      priceImpactPct\n      priceImpactRating\n      priceOut\n      priceIn\n      feeAmountDollars\n      pythRating {\n        price\n        color\n        __typename\n      }\n      __typename\n    }\n    price(coinTypeIn: $coinTypeIn, coinTypeOut: $coinTypeOut, amountIn: $amount)\n    __typename\n  }\n}",
                "variables": {
                    "amount": amount,
                    "coinTypeIn": token_left_address,
                    "coinTypeOut": token_right_address,
                    "poolInput": {
                        "coinTypes": [
                            token_left_address,
                            token_right_address
                        ]
                    },
                    "slippagePct": 5
                }
            }
            url = "https://mainnet.aux.exchange/graphql"
            req = requests.post(json=json_data, url=url, headers=headers, verify=False)
            ret_dict = json.loads(req.text)
            sell_price = float(ret_dict["data"]["pool"]["quoteExactIn"]["priceIn"])
            ret["sell_price"] = sell_price

            # === get buy price ===
            json_data = {
                "operationName": "PoolPriceOut",
                "query": "query PoolPriceOut($poolInput: PoolInput!, $coinTypeIn: String!, $coinTypeOut: String!, $amount: Float!, $slippagePct: Float!) {\n  pool(poolInput: $poolInput) {\n    quoteExactOut(\n      coinTypeIn: $coinTypeIn\n      coinTypeOut: $coinTypeOut\n      amountOut: $amount\n      slippagePct: $slippagePct\n    ) {\n      expectedAmountIn\n      maxAmountIn\n      maxFeeAmount\n      priceImpactPct\n      priceImpactRating\n      priceOut\n      priceIn\n      maxFeeAmountDollars\n      pythRating {\n        price\n        color\n        __typename\n      }\n      __typename\n    }\n    price(coinTypeIn: $coinTypeIn, coinTypeOut: $coinTypeOut, amountIn: $amount)\n    __typename\n  }\n}",
                "variables": {
                    "amount": amount,
                    "coinTypeIn": token_right_address,
                    "coinTypeOut": token_left_address,
                    "poolInput": {
                        "coinTypes": [
                            token_right_address,
                            token_left_address
                        ]
                    },
                    "slippagePct": 5
                }
            }
            req = requests.post(json=json_data, url=url, headers=headers)
            ret_dict = json.loads(req.text)
            buy_price = float(ret_dict["data"]["pool"]["quoteExactOut"]["priceOut"])
            ret["buy_price"] = buy_price
            # print(f"[{time.asctime(time.localtime(time.time()))} Log] on chain sell price: {sell_price}, buy price: {buy_price}")
            return ret
        except Exception as e:
            print(e.args)
            time.sleep(2)
            continue

