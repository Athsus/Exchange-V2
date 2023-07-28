
# TODO test
import json

import requests
import web3 as web3
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

    try:
        price = (data["buy_pred"] + data["sell_pred"]) / 2
    except Exception:
        price = data["fake_price"]

    amount_1 = amount
    amount_2 = amount / price
    # buy
    fromTokenAddress = token_right_address
    toTokenAddress = token_left_address
    url = "https://api.1inch.io/v5.0/{}/quote?" \
          "fromTokenAddress={}" \
          "&toTokenAddress={}" \
          "&amount={}".format(chain_id, fromTokenAddress, toTokenAddress,
                              str(int(10 ** token_right_decimals * amount_1)))
    req = requests.get(url=url)
    dic = json.loads(req.text)
    if req.status_code != 200:
        raise Exception("1inch get price error： {}, {}, {}".format(dic["statusCode"], dic["error"], dic["description"]))
    ret = {}
    toAmt = int(dic["toTokenAmount"]) / (10 ** token_left_decimals)
    fromAmt = int(dic["fromTokenAmount"]) / (10 ** token_right_decimals)
    ret["buy_price"] = fromAmt / toAmt
    # 近似计算,假设手续费3%%
    ret["sell_price"] = ret["buy_price"] / 1.003 * 0.997

    return ret
    #
    # fromTokenAddress = token_left_address
    # toTokenAddress = token_right_address
    # url = "https://api.1inch.io/v5.0/{}/quote?" \
    #       "fromTokenAddress={}" \
    #       "&toTokenAddress={}" \
    #       "&amount={}".format(chain_id, fromTokenAddress, toTokenAddress,
    #                           str(int(10 ** token_left_decimals * amount_2)))
    # req = requests.get(url=url)
    # if req.status_code != 200:
    #     raise Exception("1inch get price error： {}, {}, {}".format(dic["statusCode"], dic["error"], dic["description"]))
    # dic = json.loads(req.text)
    # toAmt = int(dic["toTokenAmount"]) / (10 ** token_right_decimals)
    # fromAmt = int(dic["fromTokenAmount"]) / (10 ** token_left_decimals)
    # ret["sell_price"] = toAmt / fromAmt
    # return ret
