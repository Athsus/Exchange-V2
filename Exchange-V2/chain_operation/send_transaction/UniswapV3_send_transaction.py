import json
import time

from chain_operation.exception_handler import transaction_exception_handler

import web3

from _utils.uniswap import Uniswap
slippage = 0.05

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
    # pre reading
    nonce = data["nonce"]
    gas_price = int(data["gas_price"])
    # Convert quantity to token decimals
    quantity_wei = int(quantity * 10 ** token_left_decimals)

    with open("_utils/uniswap/assets/uniswap-v3/router.abi", "r", encoding="utf-8") as f:
        univ3_abi = json.loads(f.read())

    router_contract = web3.eth.contract(address=to, abi=univ3_abi)

    functions = router_contract.functions

    if side == 0:
        # buy
        func = functions.exactInputSingle
        hex_data = func(
            {
                "tokenIn": token_right_address,
                "tokenOut": token_left_address,
                "fee": 3000,
                "recipient": to,
                "deadline": int(time.time()) + 1000000000000000000,
                "amountIn": quantity_wei,
                "amountOutMinimum": quantity_wei / (10 ** token_left_decimals) * (10 ** token_right_decimals) * (1 - slippage),
                "sqrtPriceLimitX96": 0
            }
        ).build_transaction({
            "from": sender,
            "nonce": nonce,
            "gasPrice": gas_price,
            "gas": gas_limit,
            "chainId": chain_id
        })
    elif side == 1:
        func = functions.exactOutputSingle
        hex_data = func(
            {
                "tokenIn": token_left_address,
                "tokenOut": token_right_address,
                "fee": 3000,
                "recipient": to,
                "deadline": int(time.time()) + 1000000000000000000,
                "amountOut": quantity_wei,
                "amountInMaximum": quantity_wei / (10 ** token_left_decimals) * (10 ** token_right_decimals) * (1 + slippage),
                "sqrtPriceLimitX96": 0
            }
        ).build_transaction({
            "from": sender,
            "nonce": nonce,
            "gasPrice": gas_price,
            "gas": gas_limit,
            "chainId": chain_id,
        })
    else:
        raise Exception(f"side must be 0 or 1, now is {side}")

    signed_txn = web3.eth.account.sign_transaction(
        hex_data, private_key=signature
    )
    txn = web3.eth.send_raw_transaction(signed_txn.rawTransaction)

    return txn.hex()
