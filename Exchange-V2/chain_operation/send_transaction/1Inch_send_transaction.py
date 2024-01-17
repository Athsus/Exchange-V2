import json
import time

import requests
import web3 as web3

from chain_operation.exception_handler import transaction_exception_handler

INCH_API_KEY = "bVT1x0WvwoMlzVnnMTYW4xhFuoew6ByX"
AUTH_HEADER = {
    "Authorization": "Bearer {}".format(INCH_API_KEY)
}

def get_swap(
        my_address,
        chain_id,
        fromTokenAddress,
        toTokenAddress,
        amount,
        slippage=1
):
    """
    Swap
    return: dynamic router, data
    """
    while True:
        try:
            print("1inch: ", int(amount))
            url = f"https://api.1inch.dev/swap/v5.2/{chain_id}/swap?" \
                  f"src={fromTokenAddress}" \
                  f"&dst={toTokenAddress}" \
                  f"&amount={int(amount)}" \
                  f"&from={my_address}" \
                  f"&slippage={slippage}"

            req = requests.get(url=url, headers=AUTH_HEADER)
            if req.status_code != 200:
                raise Exception("1inch get swap error： {}, {}, {}".format(req.status_code, req.text, url))
            dic = json.loads(req.text)
            tx_data = dic["tx"]["data"]
            tx_gas_price = int(dic["tx"]["gasPrice"])
            # tx_from = dic["tx"]["from"]
            return tx_data, tx_gas_price
        except Exception as e:
            print(e.args)
            time.sleep(1)
            continue


def qty_to_amount(qty, decimal):
    amount = pow(10, decimal) * qty
    return amount


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
                     quantity: int,
                     data: dict,
                     signature: str,
                     is_multi,
                     is_sturb: bool,
                     slave_address=None,
                     slave_decimals=None,
pool=None
                     ) -> str:
    print(f"1inch side: {side}, for {quantity}")
    nonce = data["nonce"]
    gas_price = int(data["gas_price"])

    if side == 0:  # BUY
        data, _ = get_swap(sender, chain_id, token_right_address, token_left_address,
                        qty_to_amount(quantity, token_right_decimals))
    elif side == 1:
        data, _ = get_swap(sender, chain_id, token_left_address, token_right_address,
                        qty_to_amount(quantity, token_left_decimals))
    else:
        raise Exception("chain side error!")
    print("gas price = {} Gwei".format(gas_price / (10 ** 9)))
    signed_txn = web3.eth.account.sign_transaction(dict(
        nonce=nonce,
        # maxFeePerGas=gas_price,
        # maxPriorityFeePerGas=gas_price,
        gasPrice=gas_price,
        gas=gas_limit,
        chainId=chain_id,
        to=to,
        data=data,
    ),
        signature,
    )
    txn = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    return txn.hex()
