import requests
from web3 import Web3
import json
from chain_operation.exception_handler import chain_exception_catcher

from chain_operation.constants import get_balance_abi
import importlib


def isFilled(Obj):
    """判断一个地方是否填了
    """
    if Obj is None or len(Obj) == 0:
        return False
    else:
        return True


class chain_utils:
    def __init__(self, config):
        # 统一配置数据
        self.gas_limit = config["CHAIN_SETTINGS"]["GAS_LIMIT"]
        self.left_address = config["CHAIN_SETTINGS"]["LEFT_ADDRESS"]
        self.left_decimals = config["CHAIN_SETTINGS"]["LEFT_DECIMALS"]
        self.right_address = config["CHAIN_SETTINGS"]["RIGHT_ADDRESS"]
        self.right_decimals = config["CHAIN_SETTINGS"]["RIGHT_DECIMALS"]

        # 账户1配置数据
        self.fork = config["CHAIN_SETTINGS"]["FORK"]
        self.my_address = config["CHAIN_SETTINGS"]["MY_ADDRESS"]
        self.provider = config["CHAIN_SETTINGS"]["PROVIDER"]
        self.web3 = Web3(Web3.HTTPProvider(self.provider))  # provider initialize
        self.chain_id = config["CHAIN_SETTINGS"]["CHAIN_ID"]
        self.router = config["CHAIN_SETTINGS"]["ROUTER"]
        # 注意，第一个slave是考虑在左链上的, 也就是账户1所在的位置
        self.slave_address = config["CHAIN_SETTINGS"]["SLAVE_ADDRESS"]
        self.slave_decimals = config["CHAIN_SETTINGS"]["SLAVE_DECIMALS"]
        # 一般情况下，如果启用了第二个账户，那么就应该是multi，所谓multi也其实就是双对
        self.is_multi = config["CONFIG"]["MULTI_PAIR_CHAIN"]
        # 验证初始化函数
        version = config["CHAIN_SETTINGS"]["VERSION"]

        # 交易模块
        transaction_module_ = importlib.import_module(
            "chain_operation.send_transaction.{}_send_transaction".format(version))
        self._send_transaction = getattr(transaction_module_, "send_transaction")
        # 询价模块
        get_price_module_ = importlib.import_module("chain_operation.get_price.{}_get_price".format(version))
        self._get_price = getattr(get_price_module_, "get_price")
        self.__meta_key = config["CHAIN_SETTINGS"]["METAMASK_PRIVATE"]

        # 是否是多账户
        self.multi_chain_address = config["CONFIG"]["MULTI_PAIR_ADDRESS"]
        if self.multi_chain_address:
            # 账户2, 乱填不填为默认
            self.fork_2 = config["CHAIN_SETTINGS_2"]["FORK"]
            self.my_address_2 = config["CHAIN_SETTINGS_2"]["MY_ADDRESS"]  # TODO 传入参数有误
            if self.my_address_2 is None or len(self.my_address_2) == 0:
                self.my_address_2 = self.my_address
            self.provider_2 = config["CHAIN_SETTINGS"]["PROVIDER_2"]  # TODO 和上面对比
            if self.provider_2 is None or len(self.provider_2) == 0:
                self.provider_2 = self.provider
            self.web3_2 = Web3(Web3.HTTPProvider(self.provider_2))
            self.chain_id_2 = config["CHAIN_SETTINGS"]["CHAIN_ID_2"]
            if self.chain_id_2 is None or len(self.chain_id_2) == 0:
                self.chain_id_2 = self.chain_id
            self.router_2 = config["CHAIN_SETTINGS"]["ROUTER_2"]
            if isFilled(self.router_2) is False:
                self.router_2 = self.router
            # 那么显然，从地址2就是右链上的从币
            self.slave_address_2 = config["CHAIN_SETTINGS"]["SLAVE_ADDRESS_2"]
            if isFilled(self.slave_address_2) is False:
                self.slave_address_2 = self.slave_address
            self.slave_decimals_2 = config["CHAIN_SETTINGS"]["SLAVE_DECIMALS_2"]
            if isFilled(self.slave_address_2) is False:
                self.slave_decimals_2 = self.slave_decimals
            version_2 = config["CHAIN_SETTINGS"]["VERSION_2"]
            if isFilled(version_2) is False:
                version_2 = version
            # 第二个账户使用的模块
            self._send_transaction_2 = getattr(transaction_module_, "send_transaction")
            # 此变量不需要修改, 因为没用, 覆盖了没事
            get_price_module_ = importlib.import_module("chain_operation.get_price.{}_get_price".format(version))
            self._get_price_2 = getattr(get_price_module_, "get_price")
            self.__meta_key_2 = config["CHAIN_SETTINGS"]["METAMASK_PRIVATE_2"]
            if isFilled(self.__meta_key_2) is False:
                self.__meta_key_2 = self.__meta_key

        # Exchanges, LP对地址似乎是不需要更改的
        self.lp1 = config["CHAIN_SETTINGS"]["SLAVE_EXCHANGE_ADDRESS1"]
        self.lp2 = config["CHAIN_SETTINGS"]["SLAVE_EXCHANGE_ADDRESS2"]

        # print("VERSION: {}".format(version))


    @chain_exception_catcher
    def balanceOf(self, holder, token):
        """Single balanceOf function"""
        contract = self.web3.eth.contract(
            abi=get_balance_abi,
            address=token
        )
        balance = contract.functions.balanceOf(holder).call()
        return balance

    def get_liquidity(self):
        if self.is_multi:
            lp = self.lp2
        else:
            lp = self.lp1
        half_liquidity = self.balanceOf(lp, self.right_address)
        return 2 * half_liquidity

    @chain_exception_catcher
    def get_balances(self):
        """get balances
        主要是返回left和right的余额，和slave没有关系
        Return:
            left, right
        """
        # 方便维护就写两边了
        # 一般情况不传参数
        if self.fork == 2 or self.fork == 3:  # Aptos: Hippo, Aux
            url = "https://wqb9q2zgw7i7-mainnet.hasura.app/v1/graphql"
            data_json = {
                "operationName": "CoinsData",
                "query": "query CoinsData($owner_address: String, $limit: Int, $offset: Int) {\n  current_coin_balances(\n    where: {owner_address: {_eq: $owner_address}}\n    limit: $limit\n    offset: $offset\n  ) {\n    amount\n    coin_type\n    coin_info {\n      name\n      decimals\n      symbol\n      __typename\n    }\n    __typename\n  }\n}",
                "variables": {
                    "owner_address": self.my_address
                }
            }
            req = requests.post(url=url, json=data_json)
            ret_dict = json.loads(req.text)["data"]["current_coin_balances"]
            left_rest, right_rest = None, None
            for item in ret_dict:
                type_full_name = item["coin_type"]
                if type_full_name == self.left_address:
                    left_rest = float(item["amount"] / 10 ** item["coin_info"]["decimals"])
                if type_full_name == self.right_address:
                    right_rest = float(item["amount"] / 10 ** item["coin_info"]["decimals"])
            if left_rest is None or right_rest is None:
                raise Exception("cannot match all coin type")
            return left_rest, right_rest

        if self.multi_chain_address is True:
            left_contract = self.web3.eth.contract(
                abi=get_balance_abi,
                address=self.left_address,
            )
            try:
                balance = left_contract.functions.balanceOf(self.my_address).call()
            except Exception as e:
                # 我认为获取的是KLAY这样的官方代笔，无法通过合约获得
                balance = self.web3.eth.get_balance(self.my_address)
            left_rest = balance / 10 ** self.left_decimals

            right_contract = self.web3_2.eth.contract(
                abi=get_balance_abi,
                address=self.right_address,
            )
            balance = right_contract.functions.balanceOf(self.my_address_2).call()
            right_rest = balance / 10 ** self.right_decimals
            return left_rest, right_rest
        else:
            cur_address = self.my_address
            left_contract = self.web3.eth.contract(
                abi=get_balance_abi,
                address=self.left_address,
            )
            try:
                balance = left_contract.functions.balanceOf(cur_address).call()
            except Exception as e:
                # 我认为获取的是KLAY这样的官方代笔，无法通过合约获得
                balance = self.web3.eth.get_balance(cur_address)
            left_rest = balance / 10 ** self.left_decimals

            right_contract = self.web3.eth.contract(
                abi=get_balance_abi,
                address=self.right_address,
            )
            balance = right_contract.functions.balanceOf(cur_address).call()
            right_rest = balance / 10 ** self.right_decimals
            return left_rest, right_rest

    def get_nonce(self):
        """
        关于双链的情况使用：
        返回tuple，TODO: 在main改一下返回？不需要吧

        TODO: 长期：不要往main传回nonce了，传进chain的buffer里面吧
        """
        if self.fork == 2 or self.fork == 3:
            # Aptos 不需要Nonce
            return 0
        if self.multi_chain_address:
            return self.web3.eth.get_transaction_count(self.my_address, "pending"), self.web3_2.eth.get_transaction_count(self.my_address_2, "pending"),
        else:
            return self.web3.eth.get_transaction_count(self.my_address, "pending")

    def get_price(self, amount, data):
        """Get Price
        return: (dict)
        TODO: 测试

        双链对情况下，我应该用multi=false的方法获取两边price并且进行计算
        """
        if self.multi_chain_address:
            price2 = self._get_price(
                web3=self.web3_2,
                amount=amount,
                exchange_address1=self.lp2,  # 因为我是false multi，所以price2需要这样玩
                my_address=self.my_address_2,
                token_left_address=self.slave_address_2,
                token_left_decimals=self.slave_decimals_2,
                token_right_address=self.right_address,
                token_right_decimals=self.right_decimals,
                is_multichain=False
            )
            mid_amt = amount / ((price2["sell_price"] + price2["buy_price"]) / 2)
            price1 = self._get_price(
                web3=self.web3,
                amount=mid_amt,
                exchange_address1=self.lp1,
                my_address=self.my_address,
                token_left_address=self.left_address,
                token_left_decimals=self.left_decimals,
                token_right_address=self.slave_address,
                token_right_decimals=self.slave_decimals,
                is_multichain=False,

            )
            ret = {"sell_price": price1["sell_price"] * price2["sell_price"],
                   "buy_price": price1["buy_price"] * price2["buy_price"]}
            return ret
        else:
            return self._get_price(
                web3=self.web3,
                amount=amount,
                exchange_address1=self.lp1,
                exchange_address2=self.lp2,
                my_address=self.my_address,
                token_left_address=self.left_address,
                token_left_decimals=self.left_decimals,
                token_right_address=self.right_address,
                token_right_decimals=self.right_decimals,
                token_slave_address=self.slave_address,
                token_slave_decimals=self.slave_decimals,
                is_multichain=self.is_multi,
                data=data,
                chain_id=self.chain_id
            )

    def send_transaction(self,
                         side: int,
                         quantity: float,
                         data: dict,
                         is_sturb: bool
                         ) -> tuple:
        """send transaction
        在此定义接口规范，从此固定，添加则再说
        Args:
            side: "BUY":0 or "SELL":1
            quantity: 交易的普通币数量，用词同币安规范
                考虑在购买时,因为某些的router不支持类似
                exactTokenOut,你买的时候out是普通币数量，
                无法确切指定，则此时需要传入当前价值进行近似。
            data: 预处理的数据，常见参数有：nonce，gas_price，fake_price
                为了各取所需...

        没必要返回str，因为只需要打印出来就好
        """
        if self.multi_chain_address is True:
            # 解析nonce，此时是tuple
            nonce1 = data["nonce"][0]
            nonce2 = data["nonce"][1]
            data["nonce"] = nonce1

            # 麻烦的是quantity，不仅会导致不平仓，而且会有延迟
            # TODO： 怎么办？我是考虑交易完后再看需要交易多少吗？
            txn1 = self._send_transaction(
                web3=self.web3,
                side=side,
                sender=self.my_address,
                to=self.router,
                chain_id=self.chain_id,
                token_left_address=self.left_address,
                token_left_decimals=self.left_decimals,
                token_right_address=self.slave_address,
                token_right_decimals=self.slave_decimals,
                gas_limit=self.gas_limit,
                quantity=quantity,  # 这个还好，还得看顺序，方向...TODO
                data=data,
                signature=self.__meta_key,
                is_multi=False,
            )

            data["nonce"] = nonce2
            txn2 = self._send_transaction_2(
                web3=self.web3_2,
                side=side,
                sender=self.my_address_2,
                to=self.router_2,
                chain_id=self.chain_id_2,
                token_left_address=self.slave_address_2,
                token_left_decimals=self.slave_decimals_2,
                token_right_address=self.right_address,
                token_right_decimals=self.right_decimals,
                gas_limit=self.gas_limit,
                quantity=quantity,  # 不妙啊...TODO
                data=data,
                signature=self.__meta_key_2,
                is_multi=False,
            )
            return txn1, txn2
        else:
            txn = self._send_transaction(
                web3=self.web3,
                side=side,
                sender=self.my_address,
                to=self.router,
                chain_id=self.chain_id,
                token_left_address=self.left_address,
                token_left_decimals=self.left_decimals,
                token_right_address=self.right_address,
                token_right_decimals=self.right_decimals,
                gas_limit=self.gas_limit,
                quantity=quantity,
                data=data,
                signature=self.__meta_key,
                is_multi=self.is_multi,
                slave_address=self.slave_address,
                slave_decimals=self.slave_decimals,
                is_sturb=is_sturb,
                pool=self.lp1
            )
            return txn


if __name__ == "__main__":
    import json

    with open("../../saves/config.json", 'r', encoding='utf8') as fp:
        config = json.load(fp)
    temp = chain_utils(config)

    print("?")
