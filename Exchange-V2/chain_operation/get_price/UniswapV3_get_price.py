"""
api ref: "https://github.com/uniswap-python/uniswap-python"
2023/7/27
"""

import web3

from _utils.uniswap import Uniswap

uni = None

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
    global uni
    if uni is None:
        uni = Uniswap(address=my_address, private_key=None, version=3, web3=web3)

    fake_price = (data["sell_pred"] + data["buy_pred"]) / 2

    left_amount = int(amount / fake_price * 10 ** token_left_decimals)
    ret_right = uni.get_price_input(
        token0=token_left_address,
        token1=token_right_address,
        qty=left_amount,
        fee=3000
    )
    sell_price = ret_right / 10 ** token_right_decimals / (amount / fake_price)


    right_amount = int(amount * 10 ** token_right_decimals)
    ret_left = uni.get_price_input(
        token0=token_right_address,
        token1=token_left_address,
        qty=right_amount,
        fee=3000
    )
    buy_price = amount / (ret_left / 10 ** token_left_decimals)

    return {"sell_price": sell_price, "buy_price": buy_price}
