import requests
import time

from _utils.log import log
from chain_operation import constants
from chain_operation.constants import HEADER
from chain_operation.exception_handler import transaction_exception_handler
import web3

from chain_operation.gas_price_optimize.get_gas_price import get_gas_price


def send_transaction(**components):
    log.info("Open ocean sending transaction")
    web3_object: web3.Web3 = components["web3"]
    chain_id = components["chain_id"]
    pre_processed_data = components["data"]
    nonce = pre_processed_data["nonce"]
    # 判断gas price小数部分有没有值，如果有，那么成为float，否则int
    gas_price = pre_processed_data["gas_price"]
    side = components["side"]
    chain_name = constants.chain_list[str(chain_id)]

    # TOKEN ADDRESSES AND DECIMALS
    token_left_address = components["token_left_address"]
    token_right_address = components["token_right_address"]
    sender = components["sender"]
    quantity = components["quantity"]

    #
    to = components["to"]
    signature = components["signature"]

    # USING OPEN OCEAN API
    base_url = f"https://open-api.openocean.finance/v3/{chain_name}/swap_quote"
    # 判断gas price小数部分有没有值，如果有，那么成为float，否则int
    if gas_price % 10 == 0:
        gas_price = int(gas_price)
    else:
        gas_price = float(gas_price)

    if side == 0:
        # buy
        in_token_address = token_right_address
        out_token_address = token_left_address
    else:
        # sell
        in_token_address = token_left_address
        out_token_address = token_right_address

    params = {
        "inTokenAddress": in_token_address,
        "outTokenAddress": out_token_address,
        "account": sender,
        "amount": "{:.10f}".format(quantity),
        "gasPrice": gas_price / 10**9,
        "slippage": 3
    }
    url = base_url + "?" + "&".join([key + "=" + str(value) for key, value in params.items()])
    MAX_RETRY = 10
    while MAX_RETRY:
        try:
            log.info("try to send transaction...")
            MAX_RETRY -= 1
            req = requests.get(url=url, headers=HEADER)
            status_code = req.json()["code"]
            if status_code != 200:
                raise Exception(send_transaction, req.text)
            req_json = req.json()
            hex_data = req_json["data"]["data"]

            optimized_gas_price = get_gas_price(chain_id)
            if optimized_gas_price is not None:
                gas_price = optimized_gas_price

            gas_limit = int(req_json["data"]["estimatedGas"])
            # Build transaction
            signed_txn = web3_object.eth.account.sign_transaction(dict(
                nonce=nonce,
                # maxFeePerGas=gas_price,
                # maxPriorityFeePerGas=gas_price,
                gasPrice=int(gas_price),
                gas=gas_limit,
                chainId=chain_id,
                to=to,
                data=hex_data,
            ),
                signature,
            )
            # Send transaction
            txn_hash = web3_object.eth.sendRawTransaction(signed_txn.rawTransaction)
            log.info("send transaction success")
            return txn_hash.hex()
        except Exception as e:
            log.warning(f"failed to send transaction: {e}, retrying")
            time.sleep(2)
    return None
