import json

import requests

from chain_operation.constants import chain_list
from chain_operation.exception_handler import transaction_exception_handler
import web3



@transaction_exception_handler
def send_transaction(web3: web3.Web3,
                     side: int,
                     sender: str,
                     to: str,
                     chain_id: int,
                     token_left_address: str,
                     token_left_decimals: int,
                     token_right_address: str,
                     token_right_decimals: int,
                     gas_limit: int,
                     quantity: float,
                     data: dict,
                     signature: str,
                     is_multi,
                     is_sturb: bool,
                     slave_address=None,
                     slave_decimals=None,
pool=None
                     ) -> str:
    if side == 0:
        # buy
        url = f"https://aggregator-api.kyberswap.com/{chain_list[str(chain_id)]}/api/v1/routes"
        amountIn = int(quantity * 10 ** token_right_decimals)
        params = {
            "tokenIn": token_right_address,
            "tokenOut": token_left_address,
            "amountIn": str(amountIn)
        }
        req = requests.get(url=url, params=params)
        res = req.json()
        if res["message"] == "successfully":
            route_summary = res["data"]["routeSummary"]
        else:
            raise Exception("KyberSwap_send_transaction.py: send_transaction() failed.")
    else:
        # sell
        url = f"https://aggregator-api.kyberswap.com/{chain_list[str(chain_id)]}/api/v1/routes"
        amountIn = int(quantity * 10 ** token_left_decimals)
        params = {
            "tokenIn": token_left_address,
            "tokenOut": token_right_address,
            "amountIn": str(amountIn)
        }
        req = requests.get(url=url, params=params)
        res = req.json()
        if res["message"] == "successfully":
            route_summary = res["data"]["routeSummary"]
        else:
            raise Exception("KyberSwap_send_transaction.py: send_transaction() failed.")

    url = f"https://aggregator-api.kyberswap.com/{chain_list[str(chain_id)]}/api/v1/route/build"
    payload = {
        "routeSummary": route_summary,
        "userAddress": sender,
        "slippage": 0.05,
        "deadline": 999999999999999,
        "recipient": sender,
    }

    headers = {
        "Content-Type": "application/json",
    }
    req = requests.post(url=url, data=json.dumps(payload), headers=headers)
    res = req.json()


    if res["message"] == "successfully":
        hex_data = res["data"]["data"]
        nonce = data["nonce"]
        gas_price = data["gas_price"]
        signed_txn = web3.eth.account.sign_transaction(dict(
            nonce=nonce,
            gasPrice=gas_price,
            gas=gas_limit,
            chainId=chain_id,
            to=to,
            data=hex_data,
        ),
            signature,
        )
        txn = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        return txn.hex()  # todo test
    else:
        raise Exception("KyberSwap_send_transaction.py: send_transaction() failed.")
