import requests
import web3

from chain_operation import constants
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

    chain_name = constants.chain_list[str(chain_id)]
    url = f"https://open-api.openocean.finance/v3/{chain_name}/quote"
    fake_price = (data["sell_pred"] + data["buy_pred"]) / 2
    left_amount = amount / fake_price
    right_amount = amount
    params = {
        "inTokenAddress": token_left_address,
        "outTokenAddress": token_right_address,
        "amount": left_amount,
        "slippage": "1",
        "gasPrice": 0.1
    }
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.82"
    }
    url = url + "?" + "&".join([key + "=" + str(value) for key, value in params.items()])
    req = requests.get(url=url, headers=header)
    status_code = req.json()["code"]
    if status_code != 200:
        raise Exception(get_price, req.text)
    req_json = req.json()

    in_amount = int(req_json["data"]["inAmount"])
    out_amount = int(req_json["data"]["outAmount"])

    w = in_amount / (10 ** token_left_decimals)
    m = out_amount / (10 ** token_right_decimals)

    sell_price = m / w

    params = {
        "inTokenAddress": token_right_address,
        "outTokenAddress": token_left_address,
        "amount": right_amount,
        "slippage": "1",
        "gasPrice": 0.1
    }
    url = f"https://open-api.openocean.finance/v3/{chain_name}/quote"
    url = url + "?" + "&".join([key + "=" + str(value) for key, value in params.items()])
    req = requests.get(url=url, headers=header)
    status_code = req.json()["code"]
    if status_code != 200:
        raise Exception(get_price, req.text)
    req_json = req.json()

    in_amount = int(req_json["data"]["inAmount"])
    out_amount = int(req_json["data"]["outAmount"])

    w = in_amount / (10 ** token_right_decimals)
    m = out_amount / (10 ** token_left_decimals)

    buy_price = w / m

    return {
        "sell_price": sell_price,
        "buy_price": buy_price
    }
