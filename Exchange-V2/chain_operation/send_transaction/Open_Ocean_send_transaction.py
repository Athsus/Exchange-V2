import requests

from _utils.log import log
from chain_operation import constants
from chain_operation.constants import HEADER
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
    chain_name = constants.chain_list[str(chain_id)]
    base_url = f"https://open-api.openocean.finance/v3/{chain_name}/swap_quote"

    nonce = data["nonce"]
    # 判断gas price小数部分有没有值，如果有，那么成为float，否则int
    gas_price = data["gas_price"]
    if gas_price % 10 == 0:
        gas_price = int(gas_price)
    else:
        gas_price = float(gas_price)

    # buy
    if side == 0:
        inTokenAddress = token_right_address
        outTokenAddress = token_left_address
    elif side == 1:
        inTokenAddress = token_left_address
        outTokenAddress = token_right_address

    params = {
        "inTokenAddress": inTokenAddress,
        "outTokenAddress": outTokenAddress,
        "account": sender,
        "amount": "{:.10f}".format(quantity),
        "gasPrice": gas_price / (10 ** 9),
        "slippage": 1
    }
    url = base_url + "?" + "&".join([key + "=" + str(value) for key, value in params.items()])
    MAX_RETRY = 10
    while MAX_RETRY:
        try:
            MAX_RETRY -= 1
            req = requests.get(url=url, headers=HEADER)
            status_code = req.json()["code"]
            if status_code != 200:
                raise Exception(send_transaction, req.text)
            req_json = req.json()
            hex_data = req_json["data"]["data"]

            # Build transaction
            signed_txn = web3.eth.account.sign_transaction(dict(
                nonce=nonce,
                maxFeePerGas=gas_price,
                maxPriorityFeePerGas=gas_price,
                # gasPrice=gas_price,
                gas=gas_limit,
                chainId=chain_id,
                to=to,
                data=hex_data,
            ),
                signature,
            )
            # Send transaction
            txn_hash = web3.eth.sendRawTransaction(signed_txn.rawTransaction)

            return txn_hash.hex()
        except Exception:
            log.warning(f"failed to send transaction, retrying")
    return None
