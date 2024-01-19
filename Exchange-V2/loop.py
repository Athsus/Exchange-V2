import datetime
import math
import os
import sys
import time
import traceback
from math import acos

from PyQt5.QtCore import QThread

import gas_tracker
from chain_operation.chain_utils import chain_utils
from errors import connection_error_handler

from _utils.thread_tool import ReturnValueThread
from send_to_your_phone.mail_handler import error_reporter, profit_reporter, reverse_warning, none_message

from _utils.log import log

eps = 1e-6


def interval(sec):
    # 显示倒计时
    for i in range(sec):
        sys.stdout.write(f'\r{i}')
        sys.stdout.flush()
        time.sleep(1)
    return


class main_loops(QThread):
    running = True

    def __init__(self, config):
        super().__init__()
        # ----------CONSTANTS------------
        # -------------CLIENTS------------
        self.exchange_target = config["CONFIG"]["EXCHANGE_TARGET"]
        if self.exchange_target == 0:  # binance
            from exchange_operation.the_binance_client import binance_client
            self.off_chain_client = binance_client(config)  # binance class
        elif self.exchange_target == 1:  # okx
            from exchange_operation.the_okx_client import okx_client
            self.off_chain_client = okx_client(config)  # okx class

        self.chain = chain_utils(config)  # chain class
        # ==OTHERS
        self.gap = config["CONFIG"]["GAP"]  # gaping period
        self.main_value = config["CONFIG"]["MAIN_QUANTITY"]  # main value( USDT )
        if self.off_chain_client.single is False:  # 非单对
            # 把main_value转为以右边币为本位的数量
            self.main_value = self.main_value / self.off_chain_client.get_ticker_price(self.off_chain_client.right + self.off_chain_client.default_stable)

        # default main quan
        self.auto_main_val = False
        if self.main_value == "auto":
            self.auto_main_val = True
            self.main_value = self.get_main_quantity()

        self.NAME = config["NAME"]
        self.normal_price_frac1 = config["CONFIG"][
            "NORMAL_PRICE_FRAC1"]  # static frac, used to calculate frac1 and frac2
        self.normal_price_frac2 = config["CONFIG"][
            "NORMAL_PRICE_FRAC2"]  # static frac, used to calculate frac1 and frac2
        self.balance_price_frac1 = config["CONFIG"]["BALANCE_PRICE_FRAC1"]
        self.balance_price_frac2 = config["CONFIG"]["BALANCE_PRICE_FRAC2"]
        self.balance_times = config["CONFIG"]["BALANCE_TIMES"]  # static
        # ---------------gas--------------
        self.gas_price = int(config["CHAIN_SETTINGS"]["GAS_PRICE"] * 10 ** 9)  # origin gas_price
        self.exec_gas_price = self.gas_price  # default to origin, notice that massive gas_price is below

        self.token_precise = self.off_chain_client.precise
        """
        You should never change the logic control vars
        """
        self.access1 = True  # access to SELL-BUY pair or not
        self.access2 = True  # access to BUY-SELL pair or not
        self.burn_out = False  # burn out order or not
        # -------------VARIABLES-----------
        self.times = 1  # order times, only used in balancing status
        self.frac1 = 1  # initial frac1 as 100%
        self.frac2 = 1  # initial frac2 as 100%
        # ==PROFIT CONTROLLER
        self.order_cnt = 0  # order counter ++
        self.summary = 0  # total profit ++
        # ==present order values
        self.cur_value1 = 0
        self.cur_value2 = 0
        # ==present MAX order values, refresh every getting status
        self.max_value1 = -1
        self.max_value2 = -1
        # ==present token / stable token, refresh every getting status
        self.rest_token = -1
        self.rest_stable = -1
        # ==nonce
        self.nonce = -1  # refresh every order complete
        # ==initial delta
        self.delta_position = 114514

        self.name = config["NAME"]

        self.stubborn_router = config["CHAIN_SETTINGS"]["STURB"]

        self.freq = [1, 1]  # 每隔多少次cnt刷新price
        self.off_price_buffer, self.on_price_buffer = {}, {}  # buffer

        # ==MASSIVE ORDER CONSTANT
        self.massive_frac = 0.0151  # 超过此frac大量交易并且gas拉高
        self.massive_value = self.main_value  # 右值可改
        self.massive_gas_price = self.gas_price  # 右值可改，你想要的gas_price, 单位Gwei


        # 总盈利率和
        self.total_profit_rate = 0
        self.lowest_profit_rate = 100
        self.highest_profit_rate = -100

        # 存储每单的内容
        self.order_record_list = []

        try:
            self.gas_strategy = config["CHAIN_SETTINGS"]["GAS_STRATEGY"]
        except Exception:
            self.gas_strategy = 0

        if self.gas_strategy == 0:
            pass
        elif self.gas_strategy == 1:  # tracker
            self.gas_tkr = gas_tracker.Gas_Price_Tracker(config)
            self.gas_tkr.track()

        self.quote_buffer = {}

    def update_exec_gas_price(self):
        """
        交易前看看最好的交易价格
        """
        if self.gas_strategy == 0:
            pass
        elif self.gas_strategy == 1:
            self.exec_gas_price = int(self.gas_tkr.last_60s_max_gas_price * 1.05)
        log.info(f"gas price is {self.exec_gas_price} at {datetime.datetime.now()}")

    def get_main_quantity(self):
        """
        如果事先设定好了，就不要动
        """
        if self.auto_main_val:
            liquidity = self.chain.get_liquidity() / 1000000
            return int(liquidity / 2000)
        else:
            return self.main_value

    def __frac_optimize_function(self, x, mid, lower_bound):
        """
        curve fraction
        """
        return round((1.8 * (mid - lower_bound) / (acos((1 / 4) - (10 / 8)) - 3.141592653589 / 2)) * (
                acos((x / 4) - (5 / 4)) - 3.141592653589 / 2), 5)

    def __frac_optimize(self, rl, rr, tic):
        """curve fraction
        """
        x = min(max(rl * tic * 10 / (rl * tic + rr), 1), 9)  # 1 <= x <= 9
        delta1 = self.__frac_optimize_function(x, self.normal_price_frac1, self.balance_price_frac1)
        delta2 = self.__frac_optimize_function(x, self.normal_price_frac2, self.balance_price_frac2)
        return round(self.normal_price_frac1 - delta1 / 2, 6), round(self.normal_price_frac2 + delta2 / 2, 6)

    def daily_report(self):
        """
        日常汇报器
        汇报内容：
        1. 盈利总量
        2. 单量
        3. 平均盈利
        4. 平均百分比
        5. 百分比极值
        """
        header = "===== Daily Report ====="
        if self.order_cnt == 0:
            none_message(header, ["今天没有交易"])
            return
        args = [
            f"{str(datetime.datetime.today())}的{self.name}"
            f"盈利了{self.summary}",
            f"跑了{self.order_cnt}单",
            f"平均每笔盈利{self.summary / self.order_cnt}",
            f"平均百分比{self.total_profit_rate / self.order_cnt}"
            f"最高百分比{self.highest_profit_rate}, 最低百分比{self.lowest_profit_rate}"
        ]
        none_message(header, args)
        # 清空
        self.order_cnt = 0
        self.summary = 0
        self.total_profit_rate = 0
        self.lowest_profit_rate = 100
        self.highest_profit_rate = -100
        return

    def get_status(self):
        """
        在初始化以及每次交易后执行，维护变量状态status
        更新变量：
        交易价值回归设定，或者根据burn值变化

        用于隐藏状态更新，免得有时候看起来 烦

        return: rest_left, rest_right
        """
        # 获取一个近似价格
        ticker_price = self.off_chain_client.get_ticker_price()
        # 获得设置交易额
        self.main_value = self.get_main_quantity()
        # 更新执行gas price
        self.exec_gas_price = self.gas_price
        # 更新剩余token
        self.rest_token, self.rest_stable = self.chain.get_balances()

        token_value = self.rest_token * ticker_price

        # refresh cur values.
        self.cur_value1 = self.main_value
        self.cur_value2 = self.main_value

        # 判断可交易方向
        # todo 如果双方都不能交易，特判
        # todo 考虑如果右边1000，左边足够，但是函数跑出去会导致access1是true，会买交易，实际上不能交易
        # if both accessible, analyze the normal situation
        if self.access1 is True and self.access2 is True:
            log.info("检查链上是否余量充足")
            # if on-chain left not enough
            if token_value < 1.05 * self.main_value:
                log.info(f"认为链上左边币不够: rest left = {token_value} < {1.05 * self.main_value}")
                # if not burning, and your token is enough to burn, then it's time to burn the rest.
                # burn mode entry
                if self.burn_out is False and token_value > self.main_value * 0.1 + 10:  # 关掉就把0.1 改成1.1
                    log.info("进入燃尽模式，双方access不变")
                    self.burn_out = True
                    # set the transaction value, it will be 10% left.
                    self.cur_value2 = token_value - self.main_value * 0.1
                    self.frac1, self.frac2 = self.__frac_optimize(self.rest_token, self.rest_stable, ticker_price)
                else:
                    # if burned, not to burn now
                    log.info("进入反弹平衡单模式")
                    if self.burn_out is True:
                        self.burn_out = False
                    self.frac1 = self.balance_price_frac1
                    self.frac2 = 114514
                    self.access2 = False
                    self.times = self.balance_times
            # on-chain stable not enough
            elif self.rest_stable < 1.05 * self.main_value:
                log.info(f"认为链上右边币不够交易: rest right = {self.rest_stable} < {1.05 * self.main_value}")
                # if not burning, and your stable is enough to burn, then it's time to burn the rest.
                if self.burn_out is False and self.rest_stable > self.main_value * 0.1 + 10:
                    log.info("进入燃尽模式，双方access不变")
                    self.burn_out = True
                    self.cur_value1 = self.rest_stable - self.main_value * 0.1  # >= 10
                    self.frac1, self.frac2 = self.__frac_optimize(self.rest_token, self.rest_stable, ticker_price)
                else:
                    # never burn and go to balance mode, access1 set to false.
                    log.info("进入反弹平衡单模式")
                    if self.burn_out is True:
                        self.burn_out = False
                    self.frac2 = self.balance_price_frac2
                    self.frac1 = 114514
                    self.access1 = False
                    self.times = self.balance_times
            else:
                # all enough
                log.info("余币充足，进入正常模式")
                self.frac1, self.frac2 = self.__frac_optimize(self.rest_token, self.rest_stable, ticker_price)
        # Exit Balance Mode
        else:
            # exists false access, so it's balance mode
            # after balance mode, it should be balanced.
            # todo if not, should I keep balance mode?
            log.info("退出反弹平衡单模式")
            self.frac1, self.frac2 = self.__frac_optimize(self.rest_token, self.rest_stable, ticker_price)
            if self.access1 is False:
                self.access1 = True
                self.times = 1  # reset
            elif self.access2 is False:
                self.access2 = True
                self.times = 1  # reset
        # 状态维护结束
        log.info("== 获取状态")
        log.info(f"== 左币数量: {self.rest_token}, 右币数量: {self.rest_stable}")
        log.info(f"== 状态: {self.access1} {self.access2} 燃烧: {self.burn_out}")
        log.info("== 下一次交易阈值: {} {}".format(self.frac1, self.frac2))
        # 更新价格buffer
        log.info(f"== 更新价格buffer")
        return self.rest_token, self.rest_stable

    def reverse_order(self, mes, qty):
        if self.off_chain_client.single is True:
            off_side = mes["side"]
            origin_quantity = float(mes["origQty"])
        else:
            off_side = mes[0]["side"]  # off_side是当前链下正常交易的side
            origin_quantity = float(mes[0]["origQty"])  # origin_quantity是当前链下正常交易的数量
        rev_side = "SELL" if off_side == "BUY" else "BUY"  # rev_side是当前链下平衡的side
        chain_rest_retry_count = 0
        while chain_rest_retry_count < 5:
            try:
                rev_mes = self.off_chain_client.marked_order(
                        side=rev_side,
                        quantity=origin_quantity
                    )
                if rev_mes:
                    reverse_warning(self.name)
                    log.info("回溯成功")
                    return
            except Exception as e:
                log.warning("回溯失败了, 因为", traceback.format_exc())
                chain_rest_retry_count += 1
                interval(15)
                continue
        
        raise Exception("回溯单失败 程序暂停")

    # todo 把profit calculator的代码拆分出来，写成一个函数，然后在这里调用
    def __profit_calculator(self, txn, mes, previous_rest_left, previous_rest_right, qty):
        """
        首先，如果币安交易失败，抛出异常并且停止程序。
        OKX交易所不适用这个函数

        1. 有效性检查
        （对山寨-山寨的检查，同样适用以下规则）

        进行五次检验。
        如果txn是none，则立刻revert，并且退出检验。
        如果链上余额不变化，那么等待一段时间，再检验。
        超过五次检验，则立刻revert，退出检验。

        每次循环更新余量，获得余额变化，并且在此之前需要正确获取币安真正的方向

        2. 计算盈利

        """
        # 币安交易失败太离谱了，直接抛出异常
        if mes is None:
            raise Exception("Binance mes is None，币安交易失败")

        # OKX特判不进行检测
        if self.exchange_target == 1:
            return previous_rest_left, previous_rest_right, 0

        # 1. 有效性检查
        # 尝试五次，如果依然失败，那么就根据单的模式回溯
        chain_rest_retry_count = 0  # 初始化单的回溯次数
        # 根据链下单的模式判断实际side，注意山寨对山寨模式的side是[0]["side"]
        if self.off_chain_client.single is True:
            off_side = mes["side"]
            origin_quantity = float(mes["origQty"])
        else:
            off_side = mes[0]["side"]  # off_side是当前链下正常交易的side
            origin_quantity = float(mes[0]["origQty"])  # origin_quantity是当前链下正常交易的数量

        rev_side = "SELL" if off_side == "BUY" else "BUY"  # rev_side是当前链下平衡的side
        log.info(f"币安交易的方向为: {off_side}")
        while self.running:  # 实际上为True
            try:
                # 检测次数大于等于5，那么认为失败了
                if chain_rest_retry_count >= 5:
                    log.warning("获取链上链下交易数量次数超过5, 即将回溯。")
                    # 反向交易单
                    self.off_chain_client.marked_order(
                        side=rev_side,
                        quantity=origin_quantity
                    )
                    reverse_warning(self.name)
                    return previous_rest_left, previous_rest_right, 0

                # 等待时间
                if chain_rest_retry_count > 1:  # 第一次不等待
                    wait_interval = 15
                    log.info(f"等待链上交易 {wait_interval}s")
                    interval(wait_interval)

                chain_rest_retry_count += 1

                # 每次交易结束一定要做的事情
                log.info(f"获取链上链下交易数量: 第{chain_rest_retry_count}次尝试")
                rest_left_token, rest_right_token = self.get_status()

                # 判定在下
                if txn is None:
                    # 如果链上没有txn，直接反向交易
                    log.warning("TXN is None, 链上交易情况堪忧, 即将回溯")
                    # 反向交易单
                    self.off_chain_client.marked_order(
                        side=rev_side,
                        quantity=origin_quantity
                    )
                    reverse_warning(self.name)
                    return previous_rest_left, previous_rest_right, 0

                delta_left = abs(rest_left_token - previous_rest_left)  # 链上山寨币的变化量
                delta_right = abs(rest_right_token - previous_rest_right)  # 链上稳定币变化量
                log.info(f"链上余额变化: {delta_left}, {delta_right}")
                # 判断链上余额是否变化
                if delta_left < 0.004 or delta_right < 0.004:
                    log.warning(f"余额没有任何变化: 原余额:({previous_rest_left}, {previous_rest_right}), 现余额:({rest_left_token}, {rest_right_token})")
                    continue

                break
            except Exception as e:
                log.warning("检查失败了, 因为", e)
                continue

        log.info("认为交易成功")

        # 特判山寨对山寨不计算盈利，返回
        if self.off_chain_client.single is False:
            log.info(f"""山寨对山寨不进行盈利计算""")
            return previous_rest_left, previous_rest_right, 0


        # 2. 计算盈利
        # 获取内容
        off_avg_price, cum_quote = self.off_chain_client.average_calculator(mes)  # 链下单的均价和数量
        # is valid order
        log.info("========ORDER {} SUMMARY========".format(self.order_cnt))
        log.info("== TXN HASH: {}".format(txn))
        delta = delta_right - cum_quote
        if (off_side == "SELL" and delta > 0) or (off_side == "BUY" and delta < 0):
            log.info("==== DEC: {}".format(-1 * abs(delta)))
            para = -1
        else:
            log.info("==== INC: {}".format(abs(delta)))
            para = 1
        if off_side == "SELL":
            temp_mes = "买"
        else:
            temp_mes = "卖"
        profit_rate = (para * (abs(delta)) / self.main_value)
        self.total_profit_rate += profit_rate
        self.highest_profit_rate = min(self.highest_profit_rate, profit_rate)
        self.lowest_profit_rate = max(self.lowest_profit_rate, profit_rate)
        log.info(f"单笔盈利/亏损百分比: {profit_rate:8.2%} 此单是链上{temp_mes}单")
        return rest_left_token, rest_right_token, para * abs(delta)

    def __sync_get_price(self, cnt):
        """
        cnt: order计数(int)

        在self.freq指定频率，根据频率取模

        """
        if cnt % self.freq[0] == 0:
            depth_get_price_thread = ReturnValueThread(target=self.off_chain_client.pred_market_price,
                                                       args=(self.times, self.main_value))
            depth_get_price_thread.start()
            binance_data = depth_get_price_thread.join()
            self.off_price_buffer = binance_data
        if cnt % self.freq[1] == 0:
            chain_thread = ReturnValueThread(target=self.chain.get_price, args=(self.times * self.main_value, binance_data))
            chain_thread.start()
            chain_data = chain_thread.join()
            self.on_price_buffer = chain_data
        return True

    def __sync_order(self, towards, nonce, binance_data):
        """
        双线程并发交易
        交易模型如下：
        <token, stable>
        (0, inf)                                                (inf, 0)
        ||============================================================||
        <== to left :2                                  1: to right ==>
        We Assume Operation "BUY" as 0, "SELL" as 1(to easily revert by bitxor)
        """
        log.info("[Order Triggering... at {}]".format(datetime.datetime.now()))
        self.update_exec_gas_price()  # 更新最好的gas
        if towards == 1:
            # 链上买，币安卖
            on_side = 0
            off_side = "SELL"
            cur_value = self.times * self.cur_value1
            price = (binance_data["sell_pred"] + binance_data["buy_pred"]) / 2
            if isinstance(self.token_precise, tuple):
                quantity = round(cur_value / price, self.token_precise[0])
            else:
                quantity = round(cur_value / price, self.token_precise)
            data = {
                "nonce": nonce,
                "gas_price": self.exec_gas_price,
                "fake_price": binance_data["buy_pred"]
            }
            data.update(self.quote_buffer)
            # If the router is stubborn, only here to specify
            # 需要传参
            if self.stubborn_router:
                x = cur_value
            else:
                x = quantity
            x = round(x, 6)
            binance_order_thread = ReturnValueThread(target=self.off_chain_client.marked_order,
                                                     args=(off_side, quantity,))
            # 如果使sturb router, 传入的参数是当前的价值
            # 交易模式解释：
            # 假设当前price = 2 USDT per Token
            # 链下卖出10(quantity)个token，链上买入20(cur_value)个stable
            # 因为此类router只可以在卖出的时候指定固定quantity的token
            # 所以买入时，指定买入的USDT，模糊化了买入的数量，使得仓位保持近似0
            swap_order_thread = ReturnValueThread(target=self.chain.send_transaction,
                                                  args=(on_side, x, data, self.stubborn_router))
        else:  # towards is 2
            on_side = 1
            off_side = "BUY"
            cur_value = self.times * self.cur_value2
            price = (binance_data["sell_pred"] + binance_data["buy_pred"]) / 2
            # 如果self.token_precise是tuple
            if isinstance(self.token_precise, tuple):
                quantity = round(cur_value / price, self.token_precise[0])
            else:
                quantity = round(cur_value / price, self.token_precise)
            data = {
                "nonce": nonce,
                "gas_price": self.exec_gas_price,
                "fake_price": binance_data["sell_pred"]
            }
            data.update(self.quote_buffer)
            binance_order_thread = ReturnValueThread(target=self.off_chain_client.marked_order,
                                                     args=(off_side, quantity,))
            swap_order_thread = ReturnValueThread(target=self.chain.send_transaction,
                                                  args=(on_side, quantity, data, self.stubborn_router))
        swap_order_thread.start()
        binance_order_thread.start()
        txn, suc = swap_order_thread.join()
        mes = binance_order_thread.join()
        return txn, suc, mes, quantity

    def get_max_values(self, ticker_price):
        """
        更新获取当前两种方向可以交易的最大价值
        """
        self.max_value1 = round(self.rest_stable * 0.9, 0)
        self.max_value2 = round((self.rest_token * ticker_price) * 0.9, 0)
        return self.max_value1, self.max_value2

    def massive_handler(self, opt, ticker_price):
        """
        如果当前的opt超过massive_frac, 将交易max(massive_val, max_value1/2)的量

        return: massive gas_price
        """
        if opt >= self.massive_frac:
            log.info("MASSIVE ORDER")
            self.get_max_values(ticker_price)  # 更新最大可执行value
            self.cur_value1 = min(self.massive_value, self.max_value1)  #
            self.cur_value2 = min(self.massive_value, self.max_value2)  #

            self.exec_gas_price = self.massive_gas_price
        else:
            return

    def price_trigger(self):
        if (self.frac1 * 0.85 < self.opt1 and self.access1)\
                or (self.frac2 * 0.85 < self.opt2 and self.access2):
            self.nonce = self.chain.get_nonce()  # avoid "nonce too low" error
        ticker_price = (self.off_buy + self.off_sell) / 2
        if self.frac1 < self.opt1 < 0.05 and self.access1:
            self.massive_handler(self.opt1, ticker_price)
            log.info(f"[Buy on chain, opt: {self.opt1}]")
            return self.__sync_order(1, self.nonce, self.binance_data)
        elif self.frac2 < self.opt2 < 0.05 and self.access2:
            self.massive_handler(self.opt2, ticker_price)
            log.info(f"[Sell on chain, opt: {self.opt2}]")
            return self.__sync_order(2, self.nonce, self.binance_data)
        else:
            return False

    def price_updater(self):
        self.__sync_get_price(self.loop_cnt)
        self.binance_data = self.off_price_buffer
        self.chain_data = self.on_price_buffer
        if "route" in self.chain_data.keys():
            self.quote_buffer = self.chain_data["route"]
        self.on_buy = self.chain_data["buy_price"]
        self.on_sell = self.chain_data["sell_price"]
        self.off_buy = self.binance_data["buy_pred"]
        self.off_sell = self.binance_data["sell_pred"]
        self.opt1 = ((self.off_sell - self.on_buy) / self.on_buy)
        self.opt2 = ((self.on_sell - self.off_buy) / self.on_sell)
        self.opt1_max = round(max(self.opt1, self.opt1_max), 4)
        self.opt2_max = round(max(self.opt2, self.opt2_max), 4)

    def run_init(self):
        self.rest_token_left, self.rest_token_right = self.get_status()
        self.opt1_max, self.opt2_max = -1, -1
        self.nonce = self.chain.get_nonce()
        self.summary = 0
        self.loop_cnt = 0
        self.reverse_cnt = 0

    def every_loop_message(self):
        spread_message = f"[{datetime.datetime.now()}] {self.opt1:8.2%} {self.opt2:8.2%} " \
                         f"max[{self.opt1_max:8.2%}%, {self.opt2_max:8.2%}%]\r"
        sys.stdout.write('\r' + spread_message)
        sys.stdout.flush()

    def run(self):
        """
        主进程
        """
        self.run_init()
        try:
            while self.running:
                self.price_updater()
                self.loop_cnt += 1
                self.every_loop_message()
                result = self.price_trigger()
                # if ordered
                if result:
                    txn, suc, mes, qty = result
                    if suc and mes:
                        log.info(f"交易成功")
                        # =============REFRESH NONCE=================
                        self.nonce = self.chain.get_nonce()
                        # =============REFRESH MAX1/2===============
                        self.opt1_max, self.opt2_max = -1, -1
                        self.reverse_cnt = 0
                        self.get_status()
                    else:
                        if not suc:
                            log.warning(f"啊?链上交易失败了, Txn: {txn}")
                            log.warning(f"若有Txn，那么可能是滑点问题，若无Txn，那么可能没Gas了")
                        if not mes:
                            log.warning(f"链下交易{'也' if not txn else ''}失败了")
                            raise Exception("链下交易失败了, 程序停止")
                        # revert order
                        log.warning("回溯")
                        self.reverse_order(mes, qty)
                        self.reverse_cnt += 1
                        if self.reverse_cnt > 3:
                            raise Exception("回溯次数过多，程序停止")
                    log.info(f"Gaping {self.gap}s")
                    interval(self.gap)
                    self.order_cnt += 1
                else:
                    interval(2)
                    continue

        except Exception:  # Any Exceptions Should Exit
            none_message(f"程序{self.name}停止了", [])
            log.error("程序有误")
            log.error(traceback.format_exc())
            os.system("pause")

    def close(self):
        self.running = False

