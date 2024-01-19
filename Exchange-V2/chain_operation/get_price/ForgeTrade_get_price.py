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
    url = "https://forge-router.evmosdao.xyz/quote?"
    fake_price = (data["sell_pred"] + data["buy_pred"]) / 2
    # sell
    json_data = {
        "protocols": "v3",
        "tokenInAddress": token_left_address,
        "tokenInChainId": chain_id,
        "tokenOutAddress": token_right_address,
        "tokenOutChainId": chain_id,
        "amount": str(int(amount * 10 ** token_right_decimals)),
        "type": "exactOut"
    }
    suffix_url = []
    for key, val in json_data.items():
        suffix_url.append(f'{key}={val}')
    suffix_url = '&'.join(suffix_url)

    req = requests.get(url+suffix_url)
    if req.status_code != 200:
        raise Exception(f"{req.text}")
    sell_req_js = req.json()
    ret_amt = int(sell_req_js['amount'])
    ret_quote = int(sell_req_js['quote'])
    sell_price = (ret_amt / ret_quote) * 10 ** (token_left_decimals - token_right_decimals)

    # buy
    json_data = {
        "protocols": "v3",
        "tokenInAddress": token_right_address,
        "tokenInChainId": chain_id,
        "tokenOutAddress": token_left_address,
        "tokenOutChainId": chain_id,
        "amount": str(int(amount * 10 ** token_right_decimals)),
        "type": "exactIn"
    }
    tail = []
    for key, val in json_data.items():
        tail.append(f'{key}={val}')
    tail = '&'.join(tail)
    req = requests.get(url=url + '?' + tail)
    if req.status_code != 200:
        raise Exception(req.text)
    buy_req_js = req.json()
    ret_amt = int(buy_req_js['amount'])
    ret_quote = int(buy_req_js['quote'])
    buy_price = (ret_amt / ret_quote) * 10 ** (token_left_decimals - token_right_decimals)

    return {
        "sell_price": sell_price,
        "buy_price": buy_price,
        "route": {
            "sell_route":  sell_req_js["route"],
            "buy_route": buy_req_js["route"]
        }
    }
