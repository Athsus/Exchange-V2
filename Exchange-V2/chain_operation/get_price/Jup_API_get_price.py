import requests
import web3

from chain_operation.exception_handler import chain_exception_catcher


@chain_exception_catcher
def get_price(
        web3: web3.Web3,
        amount: int,
        exchange_address1,
        exchange_address2,
        my_address,
        token_left_address: str,
        token_left_decimals: int,
        token_right_address: str,
        token_right_decimals: int,
        token_slave_address: str,
        token_slave_decimals: int,
        is_multichain: bool,
        chain_id: int,
        data: dict) -> dict:
    base_url = "https://quote-api.jup.ag/v6/quote"

    payload = {
        "inputMint": token_left_address,
        "outputMint": token_right_address,
        "amount": int(amount * 10 ** token_left_decimals),
        "swapMode": "ExactIn"
    }
    headers = {
        'Accept': 'application/json'
    }

    url = base_url + "?" + "&".join([f"{k}={v}" for k, v in payload.items()])

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"{response.text}")
    response_js = response.json()
    in_amt = int(response_js['inAmount'])
    out_amt = int(response_js['outAmount'])
    sell_price = (out_amt / in_amt) * 10 ** (token_left_decimals - token_right_decimals)

    # sell_price
    payload = {
        "inputMint": token_right_address,
        "outputMint": token_left_address,
        "amount": int(amount * 10 ** token_left_decimals),
        "swapMode": "ExactOut"
    }
    url = base_url + "?" + "&".join([f"{k}={v}" for k, v in payload.items()])

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"{response.text}")
    response_js = response.json()
    in_amt = int(response_js['inAmount'])
    out_amt = int(response_js['outAmount'])

    buy_price = (in_amt / out_amt) * 10 ** (token_left_decimals - token_right_decimals)
    print(buy_price, sell_price)
    return {
        "buy_price": buy_price,
        "sell_price": sell_price
    }


