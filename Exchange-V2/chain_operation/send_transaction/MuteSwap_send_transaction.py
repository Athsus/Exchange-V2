import time

from chain_operation.exception_handler import transaction_exception_handler
import web3


def to_seg(number) -> str:
    """
    将一个数字转换为16进制字符串
    如果是字符串，就直接转64位填0的进制字符串
    :param number: 数字
    :param length: 长度
    :return: 16进制字符串
    """
    if isinstance(number, str):
        return number.replace("0x", "").zfill(64)
    elif isinstance(number, int) or isinstance(number, float):
        number = int(number)
        return hex(number).replace("0x", "").zfill(64)
    else:
        print(f"number type error as {type(number)}")


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
    fake_price = data["fake_price"]
    head = "0x19a13c5c"
    # buy
    if side == 0:
        input_seg = to_seg(quantity * 10 ** token_right_decimals)
        slipper_seg = to_seg(quantity * 10 ** token_left_decimals * 0.99 / fake_price)
        xc0_seg = to_seg("c0")
        self_seg = to_seg(sender)
        timestamp_seg = to_seg(int(time.time()) + 99999999999)
        x120_seg = to_seg("120")
        x2_seg = to_seg("2")
        token1_seg = to_seg(token_right_address)
        token2_seg = to_seg(token_left_address)
        tail_seg = to_seg("2") + to_seg("0").zfill(64 * 2)
    elif side == 1:
        input_seg = to_seg(quantity * 10 ** token_left_decimals)
        slipper_seg = to_seg(quantity * (10 ** token_right_decimals) * 0.99 * fake_price)
        xc0_seg = to_seg("c0")
        self_seg = to_seg(sender)
        timestamp_seg = to_seg(int(time.time()) + 99999999999)
        x120_seg = to_seg("120")
        x2_seg = to_seg("2")
        token1_seg = to_seg(token_left_address)
        token2_seg = to_seg(token_right_address)
        tail_seg = to_seg("2") + to_seg("1") + to_seg("0")
    hex_data = head + input_seg + slipper_seg + xc0_seg + self_seg + timestamp_seg + x120_seg + x2_seg + token1_seg + token2_seg + tail_seg
    # data send 出去
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
    return txn.hex()
