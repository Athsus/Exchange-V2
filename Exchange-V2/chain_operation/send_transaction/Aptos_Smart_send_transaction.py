import os

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
    if side == 0:
        command = f"ts-node typescript/src/cli.ts swap-token {token_right_address} {token_left_address} {quantity} -c ../.aptos/config.yaml"
    else:
        command = f"ts-node typescript/src/cli.ts swap-token {token_left_address} {token_right_address} {quantity} -c ../.aptos/config.yaml"
    tmp = os.popen(command).readlines()[0].split(" ")
    txn = tmp[2]
    return txn
