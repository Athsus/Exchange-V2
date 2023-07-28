import json

import web3 as web3
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
    # 进来的是价值
    chain_name = chain_list[str(chain_id)]
    fake_price = (data["sell_pred"] + data["buy_pred"]) / 2
    actual_left_amount = amount / fake_price
    url = f"https://{chain_name}.api.0x.org/swap/v1/" \
          "quote?" \
          f"buyToken={token_left_address}&sellToken={token_right_address}" \
          f"&buyAmount={int(actual_left_amount * (10 ** token_left_decimals))}" \
          f"&slippagePercentage{0.03}"
    res = requests.get(url=url)  # buy price
    if res.status_code != 200:
        _ = res.json()["validationErrors"][0]
        reason = _["reason"]
        desc = _["description"]
        raise Exception(f"0x get price failed for {reason}, {desc}")
    buy_price = float(json.loads(res.text)["guaranteedPrice"])

    url = f"https://{chain_name}.api.0x.org/swap/v1/" \
          "quote?" \
          f"buyToken={token_right_address}&sellToken={token_left_address}" \
          f"&sellAmount={int(actual_left_amount * (10 ** token_left_decimals))}" \
          f"&slippagePercentage{0.03}"
    res = requests.get(url=url)  # buy price
    if res.status_code != 200:
        _ = res.json()["validationErrors"][0]
        reason = _["reason"]
        desc = _["description"]
        raise Exception(f"0x get price failed for {reason}, {desc}")
    sell_price = float(json.loads(res.text)["guaranteedPrice"])

    ret = {
        "sell_price": sell_price,
        "buy_price": buy_price
    }
    return ret
