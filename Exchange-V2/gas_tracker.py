import threading
import time
from web3 import Web3

from logging_module import log


class Gas_Price_Tracker:
    def __init__(self, config=None):
        if config is None:
            rpc = "https://moonbeam.api.onfinality.io/public"
        else:
            rpc = config["CHAIN_SETTINGS"]["PROVIDER"]
        self.web3 = Web3(Web3.HTTPProvider(rpc))
        self.last_60s_max_gas_price = config["CHAIN_SETTINGS"]["GAS_PRICE"]

        self.is_POA_chain = False
        try:
            self.web3.eth.getBlock('latest')
        except Exception:
            self.is_POA_chain = True

    # 定义一个函数来获取当前的快速 gas price
    def __get_fast_gas_price(self):

        # 获取当前的 pending 区块

        block = self.web3.eth.getBlock('latest')

        # 计算最近 60 秒的交易列表
        recent_txns = []
        for txn in block.transactions:
            txn_block = self.web3.eth.getTransaction(txn).blockNumber
            if block.number - txn_block <= 6:  # 12 个区块为约 2 分钟
                recent_txns.append(txn)

        if recent_txns:
            gas_prices = []
            for txn in recent_txns:
                gas_price = self.web3.eth.getTransaction(txn).gasPrice
                gas_prices.append(gas_price)
            self.last_60s_max_gas_price = max(gas_prices)

    def track(self):
        """
        选择tracker但是是POA
        则不刷新，并且使用默认gas price
        """
        if self.is_POA_chain is True:
            log.info("POA chain will not track gas price")
        else:
            threading.Timer(30, self.__get_fast_gas_price).start()
