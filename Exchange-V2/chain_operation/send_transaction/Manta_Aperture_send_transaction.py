import json
import time

from chain_operation.exception_handler import transaction_exception_handler
import web3


# helpers
def _load_abi(path: str) -> str:
    with open(path) as f:
        abi: str = json.load(f)
    return abi


def int_to_hex_padding(n, pad):
    return str(hex(n)).replace("0x", '').zfill(pad)


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
    nonce = data["nonce"]
    # 判断gas price小数部分有没有值，如果有，那么成为float，否则int
    gas_price = data["gas_price"]
    if gas_price % 10 == 0:
        gas_price = int(gas_price)
    else:
        gas_price = float(gas_price)


    slipper_page = 5
    fake_price = data['fake_price']

    router_contract = web3.eth.contract(
        address=to,
        abi=_load_abi("chain_operation/abis/aper_manta_router.abi"))


    if side == 0:
        # buy, exactOutput, path originally
        pre_load_route = data["buy_route"]
        max_tokens_bought = int(quantity * fake_price * 10 ** token_right_decimals * (100 + slipper_page) / 100)
        # generate path
        path = []
        fst = 1
        for pool in pre_load_route[0]:
            if fst:
                path.append(pool["tokenIn"]['address'].replace("0x", ''))
                fst = 0
            path.append(int_to_hex_padding(int(pool["fee"]), 6))
            path.append(pool["tokenOut"]['address'].replace("0x", ''))
        path = "0x" + ''.join(path[::-1]).replace("0x", '')
        exactOutputParams = (
            path,
            sender,
            int(quantity * 10 ** token_left_decimals),
            max_tokens_bought
        )
        transaction = router_contract.functions.exactOutput(
            exactOutputParams
        ).build_transaction({
            'nonce': web3.eth.get_transaction_count(sender),
            'gasPrice': gas_price,
            'gas': gas_limit,
            'chainId': chain_id,
            # 'to': router
        })
    else:
        # sell, exactInput, path
        pre_load_route = data["sell_route"]
        min_tokens_bought = int(quantity * fake_price * 10 ** token_right_decimals * (100 - slipper_page) / 100)
        path = []
        fst = 1
        for pool in pre_load_route[0]:
            if fst:
                path.append(pool["tokenIn"]['address'].replace("0x", ''))
                fst = 0
            path.append(int_to_hex_padding(int(pool["fee"]), 6))
            path.append(pool["tokenOut"]['address'].replace("0x", ''))
        path = "0x" + ''.join(path).replace("0x", '')
        exactInputParams = (
            path,
            sender,
            int(quantity * 10 ** token_left_decimals),
            min_tokens_bought,
        )
        transaction = router_contract.functions.exactInput(
            exactInputParams
        ).build_transaction({
            'nonce': web3.eth.get_transaction_count(sender),
            'gasPrice': gas_price,
            'gas': gas_limit,
            'chainId': chain_id,
            # 'to': router
        })

    # all done
    transaction_data = transaction["data"]
    multicall_transaction = router_contract.functions.multicall(
        int(time.time()) + 300, [transaction_data]
    ).build_transaction({
        'nonce': web3.eth.get_transaction_count(sender),
        'gasPrice': gas_price,
        'gas': gas_limit,
        'chainId': chain_id,
    })

    signed_tx = web3.eth.account.sign_transaction(
        multicall_transaction,
        signature
    )
    tx = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
    print(tx.hex())

    return tx.hex()
