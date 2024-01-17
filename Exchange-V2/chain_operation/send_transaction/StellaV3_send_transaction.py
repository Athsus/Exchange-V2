import json
import math
import time

import requests

slippage = 0.05


def _load_abi(path: str) -> str:
    with open(path) as f:
        abi: str = json.load(f)
    return abi


def get_quote(
        side,
        my_address,
        amount,
        token_in_address,
        token_in_decimals,
        token_out_address,
        token_out_decimals,
        chain_id,

):
    pass


UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
headers = {
    'User-Agent': UA

}
base_url = "https://router-api.stellaswap.com/api/v2/quote/"
slipper_page = 5

def send_transaction(**components) -> str:
    """Send Transaction Uniswap V3 Simulator
    """
    # pre reading

    pre_load_data = components["data"]
    nonce = pre_load_data["nonce"]
    gas_price = int(pre_load_data["gas_price"])
    quantity = components["quantity"]
    token_left_address = components["token_left_address"]
    token_left_decimals = components["token_left_decimals"]
    token_right_address = components["token_right_address"]
    token_right_decimals = components["token_right_decimals"]
    web3 = components["web3"]
    signature = components["signature"]
    side = components["side"]
    to = components["to"]
    gas_limit = components["gas_limit"]
    chain_id = components["chain_id"]
    my_address = components["sender"]
    amount = components["quantity"]
    sender = components["sender"]
    fake_price = pre_load_data["fake_price"]
    router_contract = web3.eth.contract(
        address=to,
        abi=_load_abi("chain_operation/abis/stellav3.abi"))
    recipient = my_address
    ddl = int(time.time() + 500000)
    limitSqrtPrice = 0
    # desired_price = fake_price  # Or any other price you have calculated

    # Calculate limitSqrtPrice
    # limitSqrtPrice = int(math.sqrt(desired_price) * (2 ** 96))

    # buy
    if side == 0:
        tokenIn = token_right_address
        tokenOut = token_left_address
        amountIn = int(amount * fake_price * 10 ** token_right_decimals)
        amountOutMinimum = int(amount * 10 ** token_left_decimals * (100 - slipper_page) / 100)
    else:
        tokenIn = token_left_address
        tokenOut = token_right_address
        amountIn = int(amount * 10 ** token_left_decimals)
        amountOutMinimum = int(amount * fake_price * 10 ** token_right_decimals * (100 - slipper_page) / 100)
        amountOutMinimum = 0
    transaction = router_contract.functions.exactInputSingle(
        (tokenIn,
        tokenOut,
        recipient,
        ddl,
        amountIn,
        amountOutMinimum,
        limitSqrtPrice)
    ).build_transaction({
            'nonce': web3.eth.get_transaction_count(sender),
            'gasPrice': gas_price,
            'gas': gas_limit,
            'chainId': chain_id,
            # 'to': router
        })

    signed_tx = web3.eth.account.sign_transaction(
        transaction,
        signature
    )
    tx = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
    print(tx.hex())

    return tx.hex()



def _send_transaction(**components) -> str:
    """Send Transaction Uniswap V3 Simulator
    """
    # pre reading

    pre_load_data = components["data"]
    nonce = pre_load_data["nonce"]
    gas_price = int(pre_load_data["gas_price"])
    quantity = components["quantity"]
    token_left_address = components["token_left_address"]
    token_left_decimals = components["token_left_decimals"]
    token_right_address = components["token_right_address"]
    token_right_decimals = components["token_right_decimals"]
    web3 = components["web3"]
    signature = components["signature"]
    side = components["side"]
    to = components["to"]
    gas_limit = components["gas_limit"]
    chain_id = components["chain_id"]
    my_address = components["sender"]
    amount = components["quantity"]
    sender = components["sender"]
    fake_price = pre_load_data["fake_price"]
    router_contract = web3.eth.contract(
        address=to,
        abi=_load_abi("chain_operation/abis/stellav3.abi"))

    # BUY
    if side == 0:
        inputToken = token_right_address
        outputToken = token_left_address
        now_amt = int(amount * fake_price * 10 ** token_right_decimals)
        buy_str = f"{inputToken}/{outputToken}/{now_amt}/{my_address}/50"
        req = requests.get(url=base_url + buy_str, headers=headers)
        if req.status_code != 200:
            raise Exception(req.text)
        req_js = req.json()
        buy_data = req_js['result']['execution']


        # instructions = pre_load_data["buy_route"]["commands"]
        # inputs = pre_load_data["buy_route"]["inputs"]
        instructions, inputs = buy_data["commands"], buy_data["inputs"]
    else:
        # SELL
        inputToken = token_left_address
        outputToken = token_right_address
        now_amt = int(amount * 10 ** token_left_decimals)
        sell_str = f"{inputToken}/{outputToken}/{now_amt}/{my_address}/50"
        req = requests.get(url=base_url + sell_str, headers=headers)
        if req.status_code != 200:
            raise Exception(req.text)
        req_js = req.json()
        sell_data = req_js['result']['execution']

        # instructions = pre_load_data["buy_route"]["commands"]
        # inputs = pre_load_data["buy_route"]["inputs"]
        instructions, inputs = sell_data["commands"], sell_data["inputs"]
        # instructions = pre_load_data["sell_route"]["commands"]
        # inputs = pre_load_data["sell_route"]["inputs"]

    transaction = router_contract.functions.execute(instructions, inputs).build_transaction({
        'nonce': web3.eth.get_transaction_count(sender),
        'gasPrice': gas_price,
        'gas': gas_limit,
        'chainId': chain_id,
        # 'to': router
    })

    signed_tx = web3.eth.account.sign_transaction(
        transaction,
        signature
    )
    tx = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
    print(tx.hex())

    return tx.hex()