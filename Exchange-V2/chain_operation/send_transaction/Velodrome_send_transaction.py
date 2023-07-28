import time

import web3

from chain_operation.exception_handler import transaction_exception_handler


def get_slipper_seq(
        decimal: int,
        price: float,
        quantity: float,
        direction: bool,
        target_is_stable: bool,
        slipper_rate=20.0
) -> str:
    """
    :param: slipper_rate: (float, 10 means 10%) as it is named
    :param: decimal: (int) target token's decimal
    :param: price: (float) ticker_price or else
    :param: quantity: (int) origin token's quantity
    :param: direction: (bool) True: upperbound, False: lowerbound
    :param: target_is_stable: (bool) whether target token of sequence indicates to stables

    :return: sequence of lower bound, str, length = 64
    """
    bound = -1
    if direction:
        bound = 1

    if target_is_stable is False:
        price = 1 / price

    return str(hex(int(quantity * price * ((100 + bound * slipper_rate) / 100) * (10 ** decimal)))). \
        replace("0x", "").zfill(64)


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
                     is_multi: bool,
                     is_sturb: bool,
                     slave_address=None,
                     slave_decimals=None,
pool=None
                     ) -> str:
    """Send Transaction

    Args:
        web3: (Web3 Object) Father
        side: buy?sell?
        sender: (str)
        to: (str)
        chain_id: (int)
        token_left_address: (str)
        token_left_decimals: (int)
        token_right_address: (str)
        token_right_decimals: (int)
        gas_limit: (int)
        quantity: (int) in quantity
        data: (dict) PRE-loaded data
        signature: (str) XXXXXXXXXXXXXXX
        is_multi: (bool) True/False

        slave_address: (str)
        slave_decimals: (int)
    """
    print(f"chain: {quantity}")

    type_address_frame = "00000000000000000000000000000000000000000000000000000000000000a0" \
                         + sender.replace("0x", "").zfill(64)
    nonce = data["nonce"]
    gas_price = data["gas_price"]

    timestamp_frame = str(hex(int(time.time()) + 10000)).replace("0x", "").zfill(64)
    if side == 0:  # BUY = Swap Exact Tokens For Tokens
        buy_tail = "0000000000000000000000000000000000000000000000000000000000000001" \
                   + token_right_address.replace("0x", "").zfill(64) \
                   + token_left_address.replace("0x", "").zfill(64) \
                   + "0000000000000000000000000000000000000000000000000000000000000000"
        price_frame = str(hex(int(quantity * (10 ** token_right_decimals)))).replace("0x", "").zfill(64)
        hex_data = "0xf41766d8" + \
                   price_frame + \
                   "0000000000000000000000000000000000000000000000000000000000000001" + \
                   type_address_frame + \
                   timestamp_frame + \
                   buy_tail
    elif side == 1:  # SELL = Swap Exact Tokens For Tokens
        sell_tail = "0000000000000000000000000000000000000000000000000000000000000001" \
                    + token_left_address.replace("0x", "").zfill(64) \
                    + token_right_address.replace("0x", "").zfill(64) \
                    + "0000000000000000000000000000000000000000000000000000000000000000"
        price_frame = str(hex(int(quantity * (10 ** token_left_decimals)))).replace("0x", "").zfill(64)
        hex_data = "0xf41766d8" + \
                   price_frame + \
                   "0000000000000000000000000000000000000000000000000000000000000001" + \
                   type_address_frame + \
                   timestamp_frame + \
                   sell_tail
    else:
        raise Exception("Side Error")
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
    return txn.hex()
