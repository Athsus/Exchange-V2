
import time

from exchange_operation.exception_handler import off_chain_exception_handler

# 1. 如果需要精度判定
# 2. ticker price, 返回float  OK
# 3. 市价下单
# 4. 深度询价  OK

# 5. 记得禁用盈利计算

import exchange_operation.okex.Market_api as Market
import exchange_operation.okex.Trade_api as Trade
import exchange_operation.okex.Public_api as Public


class okx_client:

    def __init__(self, config):
        api_key = config["CONFIG"]["API_KEY"]
        secret_key = config["CONFIG"]["SECRET_KEY"]

        self.symbol = config["CONFIG"]["SYMBOL"]
        self.main_quantity = config["CONFIG"]["MAIN_QUANTITY"]

        passphrase = "Naggod123456!"  # ????

        flag = "0"
        self.marketAPI = Market.MarketAPI(api_key, secret_key, passphrase, False, "1")  # TODO: 暂时是模拟盘
        self.tradeAPI = Trade.TradeAPI(api_key, secret_key, passphrase, False, "1")
        self.publicAPI = Public.PublicAPI(api_key, secret_key, passphrase, False, flag)

        self.precise = self.get_precise()

    @off_chain_exception_handler
    def get_precise(self):
        exchange_info = self.publicAPI.get_instruments('SWAP', self.symbol)
        if exchange_info["code"] != "0":
            raise Exception("检查Symbol！")
        precise = exchange_info["data"][0]["tickSz"]
        precise = precise.replace(".", "").__len__() - 1
        return precise

    @off_chain_exception_handler
    def get_ticker_price(self, symbol=None):
        result = self.marketAPI.get_ticker(self.symbol)
        price = float(result["data"][0]["last"])  # 最新成交价
        return float(price)

    @off_chain_exception_handler
    def pred_market_price(self, times, main_quantity):
        """
        :return: ret(dict)
            sell_pred: 卖一
            buy_pred: 买一
        """
        result = self.marketAPI.get_ticker(self.symbol)
        sell_one = float(result["data"][0]["askPx"])  # 卖一
        buy_one = float(result["data"][0]["bidPx"])  # 买一
        ret = {
            "sell_pred": sell_one,
            "buy_pred": buy_one
        }
        return ret

    @off_chain_exception_handler
    def marked_order(self, side: str, quantity: int):
        """
        按照配置直接市价交易
        捕获已知可放行错误，其他任何错误应当立刻停止

        side一般是大写，okx进来要小写
        """
        print(f"okx: {quantity}")
        mes = self.tradeAPI.place_order(instId=self.symbol, tdMode='cross', side=side.lower(), posSide='short',
                                        ordType='market', sz=quantity)
        return mes