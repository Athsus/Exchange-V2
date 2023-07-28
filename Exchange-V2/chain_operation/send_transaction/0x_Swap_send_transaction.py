import json

import requests
import web3 as web3

from chain_operation.constants import chain_list
from chain_operation.exception_handler import transaction_exception_handler

chain_id = 10
chain_name = chain_list[str(chain_id)]


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
                     quantity: int,
                     data: dict,
                     signature: str,
                     is_multi,
                     is_sturb: bool,
                     slave_address=None,
                     slave_decimals=None,
pool=None
                     ) -> str:
    nonce = data["nonce"]
    gas_price = data["gas_price"]
    fake_price = data["fake_price"]
    if side == 0:  # BUY
        url = f"https://{chain_name}.api.0x.org/swap/v1/" \
              "quote?" \
              f"buyToken={token_left_address}&sellToken={token_right_address}" \
              f"&buyAmount={int(quantity * (10 ** token_left_decimals))}" \
              f"&slippagePercentage{0.03}"
        res = requests.get(url=url)  # buy price
        dict_res = json.loads(res.text)
        print("res.text")
        hex_data = dict_res["data"]
        to = web3.toChecksumAddress(dict_res["to"])

    elif side == 1:  # SELL

        url = f"https://{chain_name}.api.0x.org/swap/v1/" \
              "quote?" \
              f"buyToken={token_right_address}&sellToken={token_left_address}" \
              f"&sellAmount={int(quantity * (10 ** token_left_decimals))}" \
              f"&slippagePercentage{0.03}"
        res = requests.get(url=url)  # buy price
        dict_res = json.loads(res.text)
        hex_data = dict_res["data"]
        to = web3.toChecksumAddress(dict_res["to"])

    signed_txn = web3.eth.account.sign_transaction(dict(
        nonce=nonce,
        gasPrice=gas_price,
        # maxFeePerGas=gas_price,
        # maxPriorityFeePerGas=gas_price - 1,
        gas=gas_limit,
        chainId=chain_id,
        to=to,
        data=hex_data,
    ),
        signature,
    )
    txn = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    return txn
