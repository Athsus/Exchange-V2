import os
import time

import web3


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
                     ) -> str:
    start = time.time()
    if side == 0:  # buy
        command = f"ts-node typescript/au_/aux-ts/src/index.ts swap {quantity} BUY {token_left_address} {token_right_address}"
    else:
        command = f"ts-node typescript/au_/aux-ts/src/index.ts swap {quantity} SELL {token_left_address} {token_right_address}"
    tmp = os.system(command)
    txn = ""
    end = time.time()
    print(f"交易时差: {end - start}")
    return txn
