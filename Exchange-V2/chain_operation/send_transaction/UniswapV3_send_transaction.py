import json
import time

import requests

slippage = 0.05


def get_quote(
        my_address,
        amount,
        token_in_address,
        token_in_decimals,
        token_out_address,
        token_out_decimals,
        chain_id,

):
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        'Origin': 'https://app.uniswap.org',
        'Referer': 'https://app.uniswap.org/',
        'Content-Type': 'application/json',
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',

    }
    base_url = "https://api.uniswap.org/v2/quote"
    # sell price: exactOut: Amount
    sell_query_dict = {

        'sendPortionEnabled': True,
        'configs': [
            {"routingType": "CLASSIC",
             "protocols": ["V2", "V3", "MIXED"],
             "enableUniversalRouter": True,
             "recipient": my_address,
             }
        ],

        'amount': str(int(amount * 10 ** token_out_decimals)),
        'tokenIn': token_in_address,
        'tokenInChainId': chain_id,
        'tokenOut': token_out_address,
        'tokenOutChainId': chain_id,

        'type': 'EXACT_OUTPUT'
    }
    MAX_RETRY = 5
    while MAX_RETRY:
        MAX_RETRY -= 1
        req = requests.post(url=base_url, json=sell_query_dict, headers=headers)
        if req.status_code != 200:
            time.sleep(2)
            continue
        req_js = req.json()
        return req_js["quote"]["methodParameters"]["calldata"], req_js["quote"]["methodParameters"]["value"]
    raise Exception("链上交易失败，无法获取交易数据")


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

    # BUY
    if side == 0:
        now_data = get_quote(my_address, amount, token_right_address, token_right_decimals,
                             token_left_address, token_left_decimals,
                             chain_id)
    else:
        now_data = get_quote(my_address, amount, token_left_address, token_left_decimals,
                             token_right_address, token_right_decimals,
                             chain_id)

    hex_data, value = now_data["quote"]["methodParameters"]["calldata"], now_data["quote"]["methodParameters"]["value"]
    signed_txn = web3.eth.account.sign_transaction(dict(
        nonce=nonce,
        maxFeePerGas=gas_price,
        maxPriorityFeePerGas=gas_price,
        value=value,
        # gasPrice=gas_price,
        gas=gas_limit,
        chainId=chain_id,
        to=to,
        data=hex_data
    ),
        signature,
    )
    # Send transaction
    txn = web3.eth.sendRawTransaction(signed_txn.rawTransaction)

    return txn.hex()
