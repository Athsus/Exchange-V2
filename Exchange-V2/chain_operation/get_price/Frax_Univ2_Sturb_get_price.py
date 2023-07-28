"""
UniswapV2 send transaction
Version: 20221020
"""

import web3

from chain_operation.constants import get_balance_abi
from chain_operation.exception_handler import chain_exception_catcher


@chain_exception_catcher
def balanceOf(web3, holder, token):
    """Single balanceOf function"""
    contract = web3.eth.contract(
        abi=get_balance_abi,
        address=token
    )
    balance = contract.functions.balanceOf(holder).call()
    return balance


def get_reserves(web3, holder, token1, token2):
    return [balanceOf(web3, holder, token1), balanceOf(web3, holder, token2)]


def wei_to_quant(wei, decimals):
    quant = int(wei / (10 ** decimals))
    return quant


def quan_to_wei(quan, decimals):
    wei = int(quan * (10 ** decimals))
    return wei


def __get_price(res, amount, de1, de2):
    ret = {}
    get_left_amount = __get_amount_out__uniswap_router(quan_to_wei(amount, de2), res[1], res[0])
    buy_price = amount / (
            get_left_amount / 10 ** de1)
    sell_price = buy_price * (1 - 0.003) / (1 + 0.003)
    ret["sell_price"] = sell_price
    ret["buy_price"] = buy_price
    return ret


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
    if is_multichain is False:
        reserves = get_reserves(web3, exchange_address1, token_left_address, token_right_address)

        price = __get_price(reserves, amount, token_left_decimals, token_right_decimals)
        return price
    else:
        ret = {}
        res1 = get_reserves(web3, exchange_address1, token_left_address, token_slave_address)
        res2 = get_reserves(web3, exchange_address2, token_slave_address, token_right_address)
        price2 = __get_price(res2, amount, token_slave_decimals, token_right_decimals)
        temp_amt = amount / ((price2["sell_price"] + price2["buy_price"]) / 2)
        price1 = __get_price(res1, temp_amt, token_left_decimals, token_slave_decimals)
        ret["sell_price"] = price1["sell_price"] * price2["sell_price"]
        ret["buy_price"] = price1["buy_price"] * price2["buy_price"]
    return ret


def __get_amount_out__uniswap_router(amountIn, reserveIn, reserveOut):
    amountIn = int(amountIn)
    reserveIn = int(reserveIn)
    reserveOut = int(reserveOut)
    if amountIn <= 0 or reserveIn <= 0 or reserveOut <= 0:
        return None
    amountInWithFee = amountIn * (1000 - 0.003 * 1000)
    numerator = amountInWithFee * reserveOut
    denominator = (reserveIn * 1000) + amountInWithFee
    return numerator / denominator