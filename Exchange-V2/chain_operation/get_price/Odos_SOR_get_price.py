import requests
import web3

from chain_operation.constants import HEADER
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
    url = "https://api.odos.xyz/sor/quote/v2"
    fake_price = (data["sell_pred"] + data["buy_pred"]) / 2
    left_amount = amount / fake_price
    right_amount = amount
    params = {
        "chainId": chain_id,
        "compact": True,
        "disableRFQs": False,
        "inputTokens": [
            {
                "amount": str(int(left_amount * 10 ** token_left_decimals)),
                "tokenAddress": token_left_address
            }
        ],
        "outputTokens": [
            {
                "proportion": 1,
                "tokenAddress": token_right_address,
            }
        ],
        "referralCode": 0,
        "slippageLimitPercent": 0.3,
        "sourceBlacklist": [],
        "sourceWhitelist": [],
        "userAddr": my_address
    }
    req = requests.post(url=url, json=params)
    if req.status_code != 200:
        raise Exception(get_price, req.text)
    req_json = req.json()

    in_amount = int(req_json["inAmounts"][0])
    out_amount = int(req_json["outAmounts"][0])

    w = in_amount / (10 ** token_left_decimals)
    m = out_amount / (10 ** token_right_decimals)

    sell_price = m / w

    params = {
        "chainId": chain_id,
        "inputTokens": [
            {
                "tokenAddress": token_right_address,
                "amount": str(int(right_amount * 10 ** token_right_decimals))
            }
        ],
        "outputTokens": [
            {
                "tokenAddress": token_left_address,
                "proportion": 1
            }
        ],
        "slippageLimitPercent": 0.5,
        "userAddr": my_address
        # 添加其他新选项根据你的需要
    }

    req = requests.post(url=url, json=params, headers=HEADER)
    if req.status_code != 200:
        raise Exception(get_price, req.text)
    req_json = req.json()

    in_amount = int(req_json["inAmounts"][0])
    out_amount = int(req_json["outAmounts"][0])

    w = in_amount / (10 ** token_right_decimals)
    m = out_amount / (10 ** token_left_decimals)

    buy_price = w / m

    return {
        "sell_price": sell_price,
        "buy_price": buy_price
    }
