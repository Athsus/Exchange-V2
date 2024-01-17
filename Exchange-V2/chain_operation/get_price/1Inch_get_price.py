
# TODO test
import json

import requests
import web3 as web3
from chain_operation.exception_handler import chain_exception_catcher


INCH_API_KEY = "bVT1x0WvwoMlzVnnMTYW4xhFuoew6ByX"
AUTH_HEADER = {
    "Authorization": "Bearer {}".format(INCH_API_KEY)
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

    try:
        price = (data["buy_pred"] + data["sell_pred"]) / 2
    except Exception:
        price = data["fake_price"]

    amount_1 = amount  # buy, the amount of right token(USDT)
    amount_2 = amount / price  # sell, the amount of left token(ETH)
    # buy
    fromTokenAddress = token_right_address
    toTokenAddress = token_left_address
    url = "https://api.1inch.dev/swap/v5.2/{}/quote?" \
          "src={}" \
          "&dst={}" \
          "&amount={}".format(chain_id, fromTokenAddress, toTokenAddress,
                              int(10 ** token_right_decimals * amount_1))
    req = requests.get(url=url, headers=AUTH_HEADER)
    dic = json.loads(req.text)
    ret = {}

    toAmt = int(dic["toAmount"]) / (10 ** token_left_decimals)
    fromAmt = amount_1
    ret["buy_price"] = fromAmt / toAmt

    # sell
    fromTokenAddress = token_left_address
    toTokenAddress = token_right_address
    url = "https://api.1inch.dev/swap/v5.2/{}/quote?" \
          "src={}" \
          "&dst={}" \
          "&amount={}".format(chain_id, fromTokenAddress, toTokenAddress,
                              int(10 ** token_left_decimals * amount_2))
    req = requests.get(url=url, headers=AUTH_HEADER)
    dic = json.loads(req.text)
    toAmt = int(dic["toAmount"]) / (10 ** token_right_decimals)  # USDT
    fromAmt = amount_2  # ETH
    ret["sell_price"] = toAmt / fromAmt

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
