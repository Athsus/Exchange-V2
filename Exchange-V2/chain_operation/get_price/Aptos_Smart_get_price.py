import os
import subprocess
import time

import web3 as web3


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
    while True:
        try:
            command = f"ts-node typescript/src/cli.ts agg-info {token_right_address} {token_left_address} {amount} -c ../.aptos/config.yaml"
            buy_price = float(os.popen(command).readlines()[2])
            buy_price = 1 / buy_price
            amount = amount / buy_price
            # command = f"ts-node typescript/Exchange-V2/cli.ts agg-info {token_left_address} {token_right_address} {amount} -c ../.aptos/config.yaml"
            sell_price = buy_price / 1.0007 * 0.9993
            ret = {}
            ret["sell_price"] = sell_price
            ret["buy_price"] = buy_price
            return ret
        except Exception:
            time.sleep(2)
            continue

