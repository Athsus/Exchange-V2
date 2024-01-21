import time

from binance.futures import Futures

from exchange_operation.exception_handler import off_chain_exception_handler
from _utils.thread_tool import ReturnValueThread


def interval(sec):
    time.sleep(sec)
    return


stable_list = [
    "BUSD", "USDT", "USDC", "USD", "KSD"
]


def parse_stable_name(symbol: str):
    for name in stable_list:
        if symbol.__contains__(name):
            return name
    raise Exception("can't parse a stable name")


class binance_client:

    def __init__(self, config):
        self.symbol = config["CONFIG"]["SYMBOL"]

        # judge single or multi
        self.judge_single(self.symbol)
        # if symbol is formatted as: ETH,USDT
        if self.symbol.__contains__(','):
            # ignore single
            if self.single:
                self.symbol.replace(",", "")
            else:
                self.left = self.symbol.split(",")[0]
                self.right = self.symbol.split(",")[1]

        self.main_quantity = config["CONFIG"]["MAIN_QUANTITY"]
        self.client = Futures(key=config["CONFIG"]["API_KEY"], secret=config["CONFIG"]["SECRET_KEY"])
        self.precise = self.get_precise(self.symbol, self.single)

    def judge_single(self, symbol):
        if self.symbol.__contains__("BUSD") or self.symbol.__contains__("USDT"):
            self.single = True
        else:
            # 多对
            self.single = False
            self.default_stable = "USDT"  # 默认USDT为中间
            self.left = ""
            self.right = ""

    @off_chain_exception_handler
    def get_precise(self, symbol, is_single):
        """
        and set self.left, right

        return Tuple(precise1, precise2)
        """
        exchange_info = self.client.exchange_info()
        precise = -1
        # 特判KLAY的精度是0，你要做KLAY就不行
        # if self.symbol.__contains__("KLAY"):
        #     return 0

        if is_single is True:
            for sym in exchange_info["symbols"]:
                if sym["symbol"] == symbol:
                    precise = sym["quantityPrecision"]
            if precise == -1:
                raise Exception("大概是SYMBOL填错了罢")
            return precise
        else:
            # 从exchange_info自动解析出左token和右token
            for sym in exchange_info["symbols"]:
                sym = sym["symbol"]
                left = sym.replace("USDT", "").replace("BUSD", "")
                if symbol.__contains__(left):
                    self.left = self.left if self.left != "" else left
                    self.right = self.right if self.right != "" else symbol.replace(left, "")
                    print(f"解析的左右token: {self.left}, {self.right}")
                    # 找self.left + "USDT" 和 self.right + "USDT"的precises
                    # 从exchange info找
                    left_target_symbol = self.left + self.default_stable
                    right_target_symbol = self.right + self.default_stable
                    ret_precise_1 = -1
                    ret_precise_2 = -1
                    for sym_sub in exchange_info["symbols"]:
                        if ret_precise_2 != -1 and ret_precise_1 != -1:
                            break
                        if sym_sub["symbol"] == left_target_symbol:
                            ret_precise_1 = sym_sub["quantityPrecision"]
                        if sym_sub["symbol"] == right_target_symbol:
                            ret_precise_2 = sym_sub["quantityPrecision"]
                    if ret_precise_2 == -1 or ret_precise_1 == -1:
                        raise Exception(f"精度解析有误, 解析的币对: {self.left + self.default_stable} = {ret_precise_1}," + \
                                        f"{self.right + self.default_stable} = {ret_precise_2}")
                    return ret_precise_1, ret_precise_2

    @off_chain_exception_handler
    def get_ticker_price(self, symbol=None):
        # 如果时single, 或者指定了特定的symbol进行调用
        if self.single or symbol is not None:
            if symbol is None:
                symbol = self.symbol
            return float(self.client.ticker_price(symbol=symbol)["price"])
        else:
            t1 = ReturnValueThread(target=self.get_ticker_price, args=(self.left + self.default_stable,))
            t2 = ReturnValueThread(target=self.get_ticker_price, args=(self.right + self.default_stable,))
            t1.start()
            t2.start()
            price1 = t1.join()  # U1/T1  ETH-USDT
            price2 = t2.join()  # U2/T2  DOT-USDT
            # => 如果是ETH-DOT我计算一个ETH价值多少DOT  ETH-DOT
            return price1 / price2

    @off_chain_exception_handler
    def query_order(self):
        mes = self.client.get_all_orders(symbol=self.symbol)[-1]
        return mes

    @off_chain_exception_handler
    def marked_order(self, side, quantity):
        """
        按照配置直接市价交易
        捕获已知可放行错误，其他任何错误应当立刻停止
        """
        print(f"币安交易{quantity}的量, 方向为{side}")

        if self.single:

            mes = self.client.new_order(
                symbol=self.symbol,
                side=side,
                type="MARKET",
                quantity=quantity,
            )
            return mes
        else:
            # ETH-DOT
            # 卖quantity个ETH, 买同等价值的DOT, 是一个卖的操作
            # vice versa
            if side == "BUY":
                rev_side = "SELL"
            else:
                rev_side = "BUY"
            # 计算当前价值
            # quantity个ETH现在多少DOT
            ticker_price = self.get_ticker_price()
            quantity_2 = round(ticker_price * quantity, self.precise[1])
            # 你要买的DOT
            mes1 = self.client.new_order(
                symbol=self.left + self.default_stable,
                side=side,
                type="MARKET",
                quantity=quantity
            )
            mes2 = self.client.new_order(
                symbol=self.right + self.default_stable,
                side=rev_side,
                type="MARKET",
                quantity=quantity_2
            )
            return mes1, mes2

    @off_chain_exception_handler
    def pred_market_price(self, times, main_quantity, symbol=None):
        # 指定了币对必须走这个，无论single与否
        # 没指定那么按照single来判断
        if self.single or symbol is not None:
            if symbol is None:
                symbol = self.symbol
            mes = self.client.depth(symbol=symbol, limit=50)
            summary = 0
            sell_pred = 0
            buy_pred = 0
            for item in mes["bids"]:
                summary += float(item[1]) * float(item[0])
                if summary >= main_quantity * times:
                    buy_pred = float(item[0])
                    break
            summary = 0
            for item in mes["asks"]:
                summary += float(item[1]) * float(item[0])
                if summary >= main_quantity * times:
                    sell_pred = float(item[0])
                    break
            # 因为我要卖，就得看别人的买n价，所以是反的
            ret = {"sell_pred": buy_pred, "buy_pred": sell_pred}
            return ret
        else:
            # 获得两个币的买卖N价，再除
            t1 = ReturnValueThread(target=self.pred_market_price, args=(times, main_quantity, self.left + self.default_stable))
            t2 = ReturnValueThread(target=self.pred_market_price, args=(times, main_quantity, self.right + self.default_stable))
            t1.start()
            t2.start()
            price1 = t1.join()  # U1/T1  ETH-USDT
            price2 = t2.join()  # U2/T2  DOT-USDT
            # => 如果是ETH-DOT我计算一个ETH价值多少DOT  ETH-DOT
            return {"sell_pred": price1["buy_pred"] / price2["sell_pred"], "buy_pred": price1["sell_pred"] / price2["buy_pred"]}


    @off_chain_exception_handler
    def average_calculator(self, mes):
        """
        return: (avg price, cum quote)
        """
        mes = self.query_order()
        return float(mes["avgPrice"]), float(mes["cumQuote"])

    def get_position(self) -> tuple:
        temp = self.client.account()
        for position in temp["positions"]:
            symbol = position["symbol"]
            if symbol == self.symbol:
                return float(position["positionAmt"]), float(position["notional"])
        return 0, 0

    def get_margin(self) -> float:
        temp = self.client.account()
        total_margin_balance = float(temp["totalMarginBalance"])
        return total_margin_balance
