import json

from chain_operation.exception_handler import transaction_exception_handler
import web3

swap_router_address = "0x17Ac28a29670e637c8a6E1ec32b38fC301303E34"
# exact input and output abi
# 这里的input output exact的主角是自己，不是router
exactInput_abi = {
    "type": "function",
    "name": "exactInputSingle",
    "inputs": [
        {
            "name": "tokenIn",
            "type": "address"
        },
        {
            "name": "amountIn",
            "type": "uint256"
        },
        {
            "name": "amountOutMinimum",
            "type": "uint256"
        },
        {
            "name": "pool",
            "type": "address"
        },
        {
            "name": "to",
            "type": "address"
        },
        {
            "name": "unwrap",
            "type": "bool"
        },
        {
            "name": "deadline",
            "type": "uint256"
        }
    ],
    "outputs": [
        {
            "name": "amountOut",
            "type": "uint256"
        }
    ],
    "stateMutability": "payable"
}


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
    """
    SyncSwap_send_transaction
    """
    fake_price = data["fake_price"]
    gas_price = data["gas_price"]
    nonce = data["nonce"]

    now_pool = pool
    hex_data = ""
    if side == 1:
        pass
    elif side == 0:
        # exactInputSingle
        # sell
        head = "0xc07f5c32"
        tokenIn = token_left_address[2:].zfill(64)
        amountIn = hex(int(quantity * 10 ** token_left_decimals))[2:].zfill(64)
        amountOutMinimum = "".zfill(64) # hex(int(quantity * fake_price * 10 ** token_right_decimals * 0.95))[2:].zfill(64)
        _sender = sender[2:].zfill(64)
        pool = pool[2:].zfill(64)
        tail = "".zfill(64)  # False

    hex_data = head + tokenIn + amountIn + amountOutMinimum + pool + _sender + tail

    # Build transaction
    transaction = {
        "from": sender,
        "to": swap_router_address,
        "value": 0,
        "gas": gas_limit,
        "gasPrice": int(gas_price),
        "nonce": nonce,
        "chainId": chain_id,
        "data": hex_data
    }

    # Sign transaction
    signed_tx = web3.eth.account.sign_transaction(transaction, signature)

    # Send transaction
    try:
        tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
        return tx_hash.hex()
    except Exception as e:
        if e.args[0]["code"] == -32000:
            print("transaction failed,", e.args[0]["message"])
            return None
        print(e)
        return None
