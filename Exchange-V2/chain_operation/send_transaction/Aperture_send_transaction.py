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
    nonce = data["nonce"]
    # 判断gas price小数部分有没有值，如果有，那么成为float，否则int
    gas_price = data["gas_price"]
    if gas_price % 10 == 0:
        gas_price = int(gas_price)
    else:
        gas_price = float(gas_price)

    slipper_page = 1
    fake_price = data['fake_price']
    # construct hex data
    sell_data = "0x5ae401dc" \
           "000000000000000000000000000000000000000000000000099999996555940b" \
           "0000000000000000000000000000000000000000000000000000000000000040" \
           "0000000000000000000000000000000000000000000000000000000000000001" \
           "0000000000000000000000000000000000000000000000000000000000000020" \
           "00000000000000000000000000000000000000000000000000000000000000e4" \
           "04e45aaf" \
           f"{token_left_address.replace('0x', '').zfill(64)}" \
           f"{token_right_address.replace('0x', '').zfill(64)}" \
           f"00000000000000000000000000000000000000000000000000000000000001f4" \
           f"0000000000000000000000000000000000000000000000000000000000000001" \
           f"{str(hex(int(quantity * 10 ** token_right_decimals))).replace('0x', '').zfill(64)}" \
           f"{str(hex(int((quantity * fake_price * ((100 - slipper_page) / 100)) * 10 ** token_right_decimals))).replace('0x', '').zfill(64)}" \
           f"0000000000000000000000000000000000000000000000000000000000000000" \
           f"00000000000000000000000000000000000000000000000000000000"
    buy_data = "0x5ae401dc" \
           "000000000000000000000000000000000000000000000000099999996555940b" \
           "0000000000000000000000000000000000000000000000000000000000000040" \
           "0000000000000000000000000000000000000000000000000000000000000001" \
           "0000000000000000000000000000000000000000000000000000000000000020" \
           "00000000000000000000000000000000000000000000000000000000000000e4" \
           "04e45aaf" \
           f"{token_right_address.replace('0x', '').zfill(64)}" \
           f"{token_left_address.replace('0x', '').zfill(64)}" \
           f"00000000000000000000000000000000000000000000000000000000000001f4" \
           f"0000000000000000000000000000000000000000000000000000000000000001" \
           f"{str(hex(int(quantity * 10 ** token_right_decimals))).replace('0x', '').zfill(64)}" \
           f"{str(hex(int((quantity * fake_price * ((100 + slipper_page) / 100)) * 10 ** token_right_decimals))).replace('0x', '').zfill(64)}" \
           f"0000000000000000000000000000000000000000000000000000000000000000" \
           f"00000000000000000000000000000000000000000000000000000000"
    signed_txn = web3.eth.account.sign_transaction(dict(
        nonce=nonce,
        # maxFeePerGas=gas_price,
        # maxPriorityFeePerGas=gas_price,
        gasPrice=gas_price,
        gas=gas_limit,
        chainId=chain_id,
        to=to,
        data=sell_data if side == 0 else buy_data,
    ),
        signature,
    )
    # Send transaction
    txn_hash = web3.eth.sendRawTransaction(signed_txn.rawTransaction)

    return txn_hash.hex()
