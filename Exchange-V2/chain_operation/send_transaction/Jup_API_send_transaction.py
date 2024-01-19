import base64
import json
import time

from solana.rpc.api import Client

import requests
from solana.rpc.commitment import Commitment
from solana.rpc.core import RPCException
from solders import message
from solders.transaction import VersionedTransaction, Transaction as solderTransaction
from solders.keypair import Keypair

from _utils.log import log
from chain_operation.exception_handler import transaction_exception_handler
import web3

LAMPORTS_PER_SOL = 1000000000

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
    quote_url = "https://quote-api.jup.ag/v6/quote"
    swap_url = "https://quote-api.jup.ag/v6/swap"
    http_client = Client("https://api.mainnet-beta.solana.com", commitment=Commitment("confirmed"), timeout=30)

    # quantity = 0.000001  # debug

    user_public_key = sender
    destination_token_account = sender

    user_private_key = signature

    if side == 0:
        # buy, exactOut with quantity of SOL or sth
        mode = "ExactOut"
        input_mint = token_right_address
        output_mint = token_left_address
    else:
        # sell, exactIn with quantity of SOL or sth
        mode = "ExactIn"
        input_mint = token_left_address
        output_mint = token_right_address

    # quote first
    quote_payload = {
        "inputMint": input_mint,
        "outputMint": output_mint,
        "amount": str(int(quantity * 10 ** token_left_decimals)),
        "swapMode": mode
    }
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    url = quote_url + "?" + "&".join([f"{k}={v}" for k, v in quote_payload.items()])
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"{response.text}")
    response_js = response.json()
    print("quote complete")

    # get swap transaction
    swap_payload = json.dumps({
        "userPublicKey": user_public_key,
        "wrapAndUnwrapSol": True,
        "quoteResponse": response_js
    })
    swap_response = requests.request("POST", swap_url, headers=headers, data=swap_payload)
    if swap_response.status_code != 200:
        raise Exception(f"{swap_response.text}")
    print("transaction built")
    swap_response_js = swap_response.json()
    raw_transaction = base64.b64decode(swap_response_js["swapTransaction"])
    raw_tx = VersionedTransaction.from_bytes(raw_transaction)

    payer = Keypair.from_base58_string(user_private_key)

    signed_tx = payer.sign_message(message.to_bytes_versioned(raw_tx.message))

    s_signed_tx = VersionedTransaction.populate(
        raw_tx.message, [signed_tx]
    )

    # all right above
    try:
        print("Executing Transaction")
        start_time = time.time()
        txid = http_client.send_transaction(s_signed_tx)

        print(f"Transaction ID: {txid.value}")
        print(f"Transaction URL: https://solscan.io/tx/{txid.value}")

        txid_string_sig = signed_tx.from_string(str(txid.value))
        checkTxn = True
        while checkTxn:
            try:
                status = http_client.get_transaction(txid_string_sig, "jsonParsed", max_supported_transaction_version=0)
                FeesUsed = (status.value.transaction.meta.fee) / LAMPORTS_PER_SOL
                if status.value.transaction.meta.err == None:
                    print("Transaction Success")
                    print("Transaction Fees: {:.10f} SOL".format(FeesUsed))

                    end_time = time.time()
                    execution_time = end_time - start_time
                    print(f"Execution time: {execution_time} seconds")

                    checkTxn = False
                    txnBool = False

                    return str(txid.value)
                else:
                    print("Transaction Failed: ", status.value.transaction.meta.err)

                    end_time = time.time()
                    execution_time = end_time - start_time
                    print(f"Execution time: {execution_time} seconds")

                    checkTxn = False
            except Exception as e:
                log.warning(f"Transaction not yet success: {e}")
                time.sleep(3)
    except RPCException as e:
        log.warning(f"e|RPC ERROR {e}")
        time.sleep(1)
    except Exception as e:
        log.warning(f"e|Exception ERROR {e}")