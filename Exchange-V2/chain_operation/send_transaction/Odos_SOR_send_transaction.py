import requests
import web3 as web3

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
    req = requests.post(url=url, json=params)
    if req.status_code != 200:
        raise Exception(get_quote_path_id, req.text)
    req_json = req.json()
    return req_json["pathId"]



def get_assemble(chain_id, sender, in_addr, out_addr, dec, amount):
    path_id = get_quote_path_id(chain_id, sender, in_addr, out_addr, dec, amount)
    params = {
        "userAddr": sender,
        "pathId": path_id,
        "simulate": False
    }
    url = "https://api.odos.xyz/sor/assemble"
    req = requests.post(url=url, json=params)
    if req.status_code != 200:
        raise Exception(get_assemble, req.text)
    req_json = req.json()
    hex_data = req_json["transaction"]["data"]
    to = req_json["transaction"]["to"]
    return hex_data, to


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
    if side == 0:
        hex_data, to = get_assemble(chain_id, sender, token_left_address, token_right_address, token_left_decimals,
                                    quantity)
    elif side == 1:
        hex_data, to = get_assemble(chain_id, sender, token_right_address, token_left_address, token_right_decimals,
                                    quantity)

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