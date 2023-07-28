from chain_operation.exception_handler import transaction_exception_handler
import web3
import json


def tail_constructor(self_address, token, side) -> str:
    self_address_frame = self_address.replace("0x", "").zfill(64)
    token_frame = token.replace("0x", "").zfill(64)
    if side == 0:
        tail = "0000000000000000000000000000000000000000000000000000000000000100" \
                          "0000000000000000000000000000000000000000000000000000000000000060" \
                          f"{token_frame}" \
                          f"{self_address_frame}" \
                          "0000000000000000000000000000000000000000000000000000000000000001" \
                          "0000000000000000000000000000000000000000000000000000000000000000"
    else:
        tail = "0000000000000000000000000000000000000000000000000000000000000100" \
                          "0000000000000000000000000000000000000000000000000000000000000060" \
                          f"{self_address_frame}" \
                          f"{token_frame}" \
                          "0000000000000000000000000000000000000000000000000000000000000002" \
                          "0000000000000000000000000000000000000000000000000000000000000000"
    return tail

swap_abi_raw = """[{
      "inputs": [
        {
          "components": [
            {
              "components": [
                {
                  "internalType": "address",
                  "name": "pool",
                  "type": "address"
                },
                {
                  "internalType": "bytes",
                  "name": "data",
                  "type": "bytes"
                },
                {
                  "internalType": "address",
                  "name": "callback",
                  "type": "address"
                },
                {
                  "internalType": "bytes",
                  "name": "callbackData",
                  "type": "bytes"
                }
              ],
              "internalType": "struct IRouter.SwapStep[]",
              "name": "steps",
              "type": "tuple[]"
            },
            {
              "internalType": "address",
              "name": "tokenIn",
              "type": "address"
            },
            {
              "internalType": "uint256",
              "name": "amountIn",
              "type": "uint256"
            }
          ],
          "internalType": "struct IRouter.SwapPath[]",
          "name": "paths",
          "type": "tuple[]"
        },
        {
          "internalType": "uint256",
          "name": "amountOutMin",
          "type": "uint256"
        },
        {
          "internalType": "uint256",
          "name": "deadline",
          "type": "uint256"
        }
      ],
      "name": "swap",
      "outputs": [
        {
          "components": [
            {
              "internalType": "address",
              "name": "token",
              "type": "address"
            },
            {
              "internalType": "uint256",
              "name": "amount",
              "type": "uint256"
            }
          ],
          "internalType": "struct IPool.TokenAmount",
          "name": "amountOut",
          "type": "tuple"
        }
      ],
      "stateMutability": "payable",
      "type": "function"
    }]"""


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
    """
    SyncSwap_send_transaction
    """
    nonce = data["nonce"]
    gas_price = data["gas_price"]
    fake_price = data["fake_price"]

    # side == 1: 买入
    if side == 0:
        tokenIn = token_right_address
        tokenOut = token_left_address
        # quantity是已经算好的left的量
        amountIn = int(quantity * fake_price * 10 ** token_right_decimals)
        amountOutMin = int(quantity * 10 ** token_left_decimals * 0.995)
    # side == 2: 卖出
    elif side == 1:
        tokenIn = token_left_address
        tokenOut = token_right_address
        amountIn = int(quantity * 10 ** token_left_decimals)
        amountOutMin = int(quantity * fake_price * 10 ** token_right_decimals * 0.995)
    else:
        return "shit"

    # 加载SwapRouter合约的ABI
    swap_router_abi = json.loads(swap_abi_raw)

    # 设置SwapRouter合约地址和实例
    swap_router_address = web3.toChecksumAddress(to)
    swap_router_contract = web3.eth.contract(address=swap_router_address, abi=swap_router_abi)

    # 设置交易信息
    my_address = web3.toChecksumAddress(sender)
    private_key = signature

    # 创建SwapStep结构
    swap_step = {
        'pool': web3.toChecksumAddress('0x80115c708e12edd42e504c1cd52aea96c547c05c'),
        'data': b'',
        'callback': web3.toChecksumAddress("0x0000000000000000000000000000000000000000"),
        'callbackData': b'',
    }

    # amountIn = 1

    # 创建SwapPath结构
    swap_path = {
        'steps': [swap_step],
        'tokenIn': web3.toChecksumAddress(tokenIn),
        'amountIn': amountIn
    }


    # 设置其他参数
    amount_out_min = amountOutMin
    deadline = 9999999999999999999999

    # 编码函数调用
    input_data = swap_router_contract.encodeABI(
        fn_name='swap',
        args=[[swap_path], amount_out_min, deadline]
    )

    # 对input_data, 从第842个字符开始截断，并且补充为tail constructor的内容
    # BUY
    if side == 0:
        input_data = input_data[:842] + tail_constructor(my_address, token_right_address, side)
    elif side == 1:
        input_data = input_data[:842] + tail_constructor(my_address, token_left_address, side)

    # 估计Gas
    transaction = {
        'to': swap_router_address,
        'from': my_address,
        'data': input_data,
        'gas': gas_limit,
        'chainId': chain_id,  # 卡人
        # 'maxFeePerGas': gas_price,
        # 'maxPriorityFeePerGas': 100000000,
        'gasPrice': gas_price,
        'nonce': nonce
    }

    # 签署交易
    signed_tx = web3.eth.account.signTransaction(transaction, private_key)

    # 发送交易
    transaction_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)

    # 确认交易已被接收
    transaction_receipt = web3.eth.waitForTransactionReceipt(transaction_hash)

    print(f"Transaction receipt: {transaction_receipt}")
    return transaction_hash
