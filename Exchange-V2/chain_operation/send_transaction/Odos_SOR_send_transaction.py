import requests
import web3 as web3

from _utils.log import log
from chain_operation.constants import HEADER
from chain_operation.exception_handler import transaction_exception_handler
import web3


def get_quote_path_id(chain_id, sender, in_addr, out_addr, dec, amount):
    url = "https://api.odos.xyz/sor/quote/v2"
    params = {
        "chainId": chain_id,
        "inputTokens": [
            {
                "tokenAddress": in_addr,
                "amount": str(int(amount * 10 ** dec))
            }
        ],
        "outputTokens": [
            {
                "tokenAddress": out_addr,
                "proportion": 1
            }
        ],
        "slippageLimitPercent": 0.5,
        "userAddr": sender
    }
    MAX_RETRY = 10
    while MAX_RETRY:
        try:
            MAX_RETRY -= 1
            log.info(f"getting path id, {MAX_RETRY} times left")
            # must complete.
            req = requests.post(url=url, json=params, headers=HEADER)
            req_json = req.json()
            return req_json["pathId"]
        except Exception as e:
            log.warning("get quote failed, retrying")
    return None



def get_assemble(chain_id, sender, in_addr, out_addr, dec, amount):
    path_id = get_quote_path_id(chain_id, sender, in_addr, out_addr, dec, amount)
    if path_id is None:
        raise Exception("get path id failed")
    params = {
        "userAddr": sender,
        "pathId": path_id,
        "simulate": False
    }
    url = "https://api.odos.xyz/sor/assemble"
    MAX_RETRY = 10
    while MAX_RETRY:
        try:
            MAX_RETRY -= 1
            log.info(f"getting assemble {MAX_RETRY} times left")
            req = requests.post(url=url, json=params, headers=HEADER)
            req_json = req.json()
            hex_data = req_json["transaction"]["data"]
            to = req_json["transaction"]["to"]
            return hex_data, to
        except Exception:
            log.warning("get quote failed, retrying")
    return None, None


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
    if side == 1:
        # buy
        hex_data, to = get_assemble(chain_id, sender, token_left_address, token_right_address, token_left_decimals,
                                    quantity)
    elif side == 0:
        hex_data, to = get_assemble(chain_id, sender, token_right_address, token_left_address, token_right_decimals,
                                    quantity)
    else:
        raise Exception(f"side error: {side}")
    if hex_data is None:
        raise Exception("get assemble failed")
    nonce = data["nonce"]
    gas_price = data["gas_price"]

    # Build transaction
    signed_txn = web3.eth.account.sign_transaction(dict(
        nonce=nonce,
        # maxFeePerGas=gas_price,
        # maxPriorityFeePerGas=gas_price,
        gasPrice=gas_price,
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