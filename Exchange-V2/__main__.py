
import sys
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QThread
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QFileDialog
from gui import Ui_Father
import json
from send_to_your_phone import mail_handler

from loop import main_loops
from logging_module import log


def is_sturb(swap_name):
    """
    每次strub的swap应添加
    any Aptos / Velodrome swap / Frax.finance / 1inch
    """
    if swap_name == 13 or swap_name == 12 or swap_name == 10 or swap_name == 2 or swap_name == 4 or swap_name == 6 or swap_name == 7 or swap_name == 9:
        return True
    else:
        return False


class Signal(QObject):
    """Redirects console output to text widget."""
    text_update = pyqtSignal(str)

    def write(self, text):
        self.text_update.emit(str(text))
        QApplication.processEvents()

    def flush(self):
        sys.__stdout__.flush()


class MyMainForm(QMainWindow, Ui_Father):
    def __init__(self, parent=None):
        super(MyMainForm, self).__init__(parent)
        self.setupUi(self)
        self.RunButton.clicked.connect(self.run)
        self.StopButton.clicked.connect(self.stop)
        self.SaveButton.clicked.connect(self.save)
        self.LoadButton.clicked.connect(self.load)
        # MULTI ADDRESS CHECKBOX INIT
        self.MULTI_ADDRESS.toggled.connect(self.multi_address_select)  # connect
        self.TAB_CHAIN2.setEnabled(self.MULTI_ADDRESS.isChecked())  # check init
        # MULTI PAIR1 CHECKBOX INIT
        self.MULTI_CHAIN.toggled.connect(self.multi_pair_chain_select)  # connect
        self.multi_pair_chain_select()
        # MULTI PAIR2 CHECKBOX INIT
        self.MULTI_CHAIN_2.toggled.connect(self.multi_pair_chain_select_2)  # connect
        self.multi_pair_chain_select_2()
        # SPECIAL FORK SELECTED
        self.FORK.currentIndexChanged.connect(self.fork_control)
        # sys std init
        # sys.stdout = Signal()
        # sys.stderr = Signal()
        # sys.stdout.text_update.connect(self.output_written)
        self.MAIN_QUANTITY.setToolTip(str(self.MAIN_QUANTITY.placeholderText()))

        self.loop_is_running = False

    def fork_control(self):
        # 如果是Hippo or Aux
        # 智能通用思路：禁用链上中间对，只留下“普通币”和“稳定币”的地址
        # Aptos特殊：提示从hex改为token symbol
        if self.FORK.currentIndex() == 2 or self.FORK.currentText() == 3:
            # 1. 改提示
            self.CONTRACT_ADDR_LEFT.setPlaceholderText("0x1::aptos_coin::AptosCoin")
            self.CONTRACT_ADDR_RIGHT.setPlaceholderText("0x5e156f1207d0ebfa19a9eeff00d62a282278fb8719f4fab3a586a0a2c0fffbea::coin::T")
            # 2. 禁用：
            self.CONTRACT_DECIMALS_LEFT.setEnabled(False)
            self.CONTRACT_DECIMALS_RIGHT.setEnabled(False)
            self.CONTRACT_DECIMALS_SLAVE.setEnabled(False)
            self.CONTRACT_ADDR_SLAVE.setEnabled(False)
            self.LP1.setEnabled(False)
            self.LP2.setEnabled(False)
            self.MULTI_CHAIN.setEnabled(False)
            ...
        else:
            # 回溯设置
            self.CONTRACT_ADDR_LEFT.setPlaceholderText("0x1234")
            self.CONTRACT_ADDR_RIGHT.setPlaceholderText("0x1234")

            self.CONTRACT_DECIMALS_LEFT.setEnabled(True)
            self.CONTRACT_DECIMALS_RIGHT.setEnabled(True)
            self.CONTRACT_DECIMALS_SLAVE.setEnabled(True)
            self.CONTRACT_ADDR_SLAVE.setEnabled(True)
            self.LP1.setEnabled(True)
            self.LP2.setEnabled(True)
            self.MULTI_CHAIN.setEnabled(True)
            # 如果选择别的，那么读取设置
            self.multi_pair_chain_select()
            self.multi_pair_chain_select_2()
            ...

    def multi_pair_chain_select(self):
        to_state = self.MULTI_CHAIN.isChecked()
        self.CONTRACT_ADDR_SLAVE.setEnabled(to_state)
        self.CONTRACT_DECIMALS_SLAVE.setEnabled(to_state)
        self.LP2.setEnabled(to_state)

    def multi_pair_chain_select_2(self):
        to_state = self.MULTI_CHAIN_2.isChecked()
        self.CONTRACT_ADDR_SLAVE_2.setEnabled(to_state)
        self.CONTRACT_DECIMALS_SLAVE_2.setEnabled(to_state)
        self.LP2_2.setEnabled(to_state)

    def multi_address_select(self):
        """当选中启用多链时，调用此

        仅控制前端内容，当触发run时，所有参数照常传输
        """
        is_checked = self.MULTI_ADDRESS.isChecked()
        if is_checked:
            self.TAB_CHAIN2.setEnabled(True)  # 这样写增强维护性
            ...
        else:
            self.TAB_CHAIN2.setEnabled(False)
            ...

    def output_written(self, text):
        cursor = self.Logger.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.Logger.setTextCursor(cursor)
        self.Logger.ensureCursorVisible()

    def load_parameters(self, path=None):
        """
        从配置文件加载到窗口
        1. 初始化参数到窗口
        2. 返回config字典
        """
        if len(path) == 0:  # cancel
            return
        if path is None or len(path[0]) == 0:
            with open("saves/config.json", 'r', encoding='utf8') as fp:
                config_dic = json.load(fp)
        else:
            with open(path, 'r', encoding='utf8') as fp:
                config_dic = json.load(fp)

        # TITLE
        self.setWindowTitle(config_dic["NAME"])
        # BINANCE
        self.SYMBOL.setText(config_dic["CONFIG"]["SYMBOL"])
        # EMAIL
        self.MAIL_ADDRESS.setText(config_dic["CONFIG"]["MAIL_ADDRESS"])

        # ACCOUNT1
        self.MY_ADDRESS.setText(config_dic["CHAIN_SETTINGS"]["MY_ADDRESS"])
        self.PROVIDER.setText(config_dic["CHAIN_SETTINGS"]["PROVIDER"])
        self.GAS_PRICE.setText(str(config_dic["CHAIN_SETTINGS"]["GAS_PRICE"]))
        self.GAS_LIMIT.setText(str(config_dic["CHAIN_SETTINGS"]["GAS_LIMIT"]))

        # SWAP1
        self.ROUTER.setText(config_dic["CHAIN_SETTINGS"]["ROUTER"])
        self.CHAIN_ID.setText(str(config_dic["CHAIN_SETTINGS"]["CHAIN_ID"]))
        self.FORK.setCurrentIndex(config_dic["CHAIN_SETTINGS"]["FORK"])

        # CONTROL PARA
        self.NORMAL_PRICE_FRAC1.setText(str(config_dic["CONFIG"]["NORMAL_PRICE_FRAC1"]))
        self.NORMAL_PRICE_FRAC2.setText(str(config_dic["CONFIG"]["NORMAL_PRICE_FRAC2"]))
        self.BALANCE_PRICE_FRAC1.setText(str(config_dic["CONFIG"]["BALANCE_PRICE_FRAC1"]))
        self.BALANCE_PRICE_FRAC2.setText(str(config_dic["CONFIG"]["BALANCE_PRICE_FRAC2"]))
        self.GAP.setText(str(config_dic["CONFIG"]["GAP"]))
        self.MULTI_CHAIN.setChecked(config_dic["CONFIG"]["MULTI_PAIR_CHAIN"])

        self.CONTRACT_ADDR_LEFT.setText(config_dic["CHAIN_SETTINGS"]["LEFT_ADDRESS"])
        self.CONTRACT_DECIMALS_LEFT.setText(str(config_dic["CHAIN_SETTINGS"]["LEFT_DECIMALS"]))
        self.CONTRACT_ADDR_RIGHT.setText(config_dic["CHAIN_SETTINGS"]["RIGHT_ADDRESS"])
        self.CONTRACT_DECIMALS_RIGHT.setText(str(config_dic["CHAIN_SETTINGS"]["RIGHT_DECIMALS"]))
        if self.MULTI_CHAIN.isChecked() is True:
            self.CONTRACT_ADDR_SLAVE.setText(config_dic["CHAIN_SETTINGS"]["SLAVE_ADDRESS"])
            self.CONTRACT_DECIMALS_SLAVE.setText(str(config_dic["CHAIN_SETTINGS"]["SLAVE_DECIMALS"]))
            self.LP1.setText(config_dic["CHAIN_SETTINGS"]["SLAVE_EXCHANGE_ADDRESS1"])
            self.LP2.setText(config_dic["CHAIN_SETTINGS"]["SLAVE_EXCHANGE_ADDRESS2"])
        else:
            self.LP1.setText(config_dic["CHAIN_SETTINGS"]["SLAVE_EXCHANGE_ADDRESS1"])

        try:
            self.exchange_target.setCurrentIndex(config_dic["CONFIG"]["EXCHANGE_TARGET"])
        except Exception:
            pass
        try:
            self.GAS_STRATEGY.setCurrentIndex(config_dic["CHAIN_SETTINGS"]["GAS_STRATEGY"])
        except Exception:
            self.GAS_STRATEGY = 0

        # 二链交易
        if self.MULTI_ADDRESS:
            # ACCOUNT1
            self.MY_ADDRESS_2.setText(config_dic["CHAIN_SETTINGS"]["MY_ADDRESS"])
            self.PROVIDER_2.setText(config_dic["CHAIN_SETTINGS"]["PROVIDER"])
            self.GAS_PRICE_2.setText(str(config_dic["CHAIN_SETTINGS"]["GAS_PRICE"]))
            self.GAS_LIMIT_2.setText(str(config_dic["CHAIN_SETTINGS"]["GAS_LIMIT"]))

            # SWAP1
            self.ROUTER_2.setText(config_dic["CHAIN_SETTINGS"]["ROUTER"])
            self.CHAIN_ID_2.setText(str(config_dic["CHAIN_SETTINGS"]["CHAIN_ID"]))
            self.FORK_2.setCurrentIndex(config_dic["CHAIN_SETTINGS"]["FORK"])

            # CONTROL PARA
            self.MULTI_CHAIN_2.setChecked(config_dic["CONFIG"]["MULTI_PAIR_CHAIN"])

            self.CONTRACT_ADDR_LEFT_2.setText(config_dic["CHAIN_SETTINGS"]["LEFT_ADDRESS"])
            self.CONTRACT_DECIMALS_LEFT_2.setText(str(config_dic["CHAIN_SETTINGS"]["LEFT_DECIMALS"]))
            self.CONTRACT_ADDR_RIGHT_2.setText(config_dic["CHAIN_SETTINGS"]["RIGHT_ADDRESS"])
            self.CONTRACT_DECIMALS_RIGHT_2.setText(str(config_dic["CHAIN_SETTINGS"]["RIGHT_DECIMALS"]))
            if self.MULTI_CHAIN_2.isChecked() is True:
                self.CONTRACT_ADDR_SLAVE_2.setText(config_dic["CHAIN_SETTINGS"]["SLAVE_ADDRESS"])
                self.CONTRACT_DECIMALS_SLAVE_2.setText(str(config_dic["CHAIN_SETTINGS"]["SLAVE_DECIMALS"]))
                self.LP1_2.setText(config_dic["CHAIN_SETTINGS"]["SLAVE_EXCHANGE_ADDRESS1"])
                self.LP2_2.setText(config_dic["CHAIN_SETTINGS"]["SLAVE_EXCHANGE_ADDRESS2"])
            else:
                self.LP1_2.setText(config_dic["CHAIN_SETTINGS"]["SLAVE_EXCHANGE_ADDRESS1"])

        self.MAIN_QUANTITY.setText(str(config_dic["CONFIG"]["MAIN_QUANTITY"]))
        return config_dic

    def set_parameter(self):
        """set the varieties and ready to run
        从输入框的东西放入config，并且保存入文件
        """
        mail_handler.receiver = self.MAIL_ADDRESS.text()  # global

        self.config["CONFIG"]["MAIL_ADDRESS"] = self.MAIL_ADDRESS.text()
        self.config["CHAIN_SETTINGS"]["MY_ADDRESS"] = self.MY_ADDRESS.text()

        self.config["CHAIN_SETTINGS"]["MY_ADDRESS_2"] = self.MY_ADDRESS_2.text()
        self.config["CONFIG"]["SYMBOL"] = self.SYMBOL.text().upper()
        self.config["CONFIG"]["NORMAL_PRICE_FRAC1"] = float(self.NORMAL_PRICE_FRAC1.text())
        self.config["CONFIG"]["NORMAL_PRICE_FRAC2"] = float(self.NORMAL_PRICE_FRAC2.text())
        self.config["CONFIG"]["BALANCE_PRICE_FRAC1"] = float(self.BALANCE_PRICE_FRAC1.text())
        self.config["CONFIG"]["BALANCE_PRICE_FRAC2"] = float(self.BALANCE_PRICE_FRAC2.text())
        self.config["CONFIG"]["GAP"] = int(self.GAP.text())
        self.config["CHAIN_SETTINGS"]["CHAIN_ID"] = int(self.CHAIN_ID.text())
        self.config["CHAIN_SETTINGS"]["CHAIN_ID_2"] = int(self.CHAIN_ID_2.text())

        self.config["CHAIN_SETTINGS"]["GAS_PRICE"] = float(self.GAS_PRICE.text())
        self.config["CHAIN_SETTINGS"]["GAS_LIMIT"] = int(self.GAS_LIMIT.text())
        self.config["CHAIN_SETTINGS"]["LEFT_ADDRESS"] = self.CONTRACT_ADDR_LEFT.text()
        self.config["CHAIN_SETTINGS"]["LEFT_DECIMALS"] = int(self.CONTRACT_DECIMALS_LEFT.text())
        self.config["CHAIN_SETTINGS"]["RIGHT_ADDRESS"] = self.CONTRACT_ADDR_RIGHT.text()
        self.config["CHAIN_SETTINGS"]["RIGHT_DECIMALS"] = int(self.CONTRACT_DECIMALS_RIGHT.text())

        self.config["CONFIG"]["MULTI_PAIR_CHAIN"] = self.MULTI_CHAIN.isChecked()  # boolean
        self.config["CONFIG"]["MULTI_PAIR_ADDRESS"] = self.MULTI_ADDRESS.isChecked()  # boolean

        if self.config["CONFIG"]["MULTI_PAIR_CHAIN"] is True:
            self.config["CHAIN_SETTINGS"]["SLAVE_ADDRESS"] = self.CONTRACT_ADDR_SLAVE.text()
            self.config["CHAIN_SETTINGS"]["SLAVE_DECIMALS"] = int(self.CONTRACT_DECIMALS_SLAVE.text())

            self.config["CHAIN_SETTINGS"]["SLAVE_EXCHANGE_ADDRESS1"] = self.LP1.text()
            self.config["CHAIN_SETTINGS"]["SLAVE_EXCHANGE_ADDRESS2"] = self.LP2.text()
        else:
            self.config["CHAIN_SETTINGS"]["SLAVE_EXCHANGE_ADDRESS1"] = self.LP1.text()
        self.config["CHAIN_SETTINGS"]["PROVIDER"] = self.PROVIDER.text()
        self.config["CHAIN_SETTINGS"]["PROVIDER_2"] = self.PROVIDER_2.text()
        self.config["CHAIN_SETTINGS"]["ROUTER"] = self.ROUTER.text()
        self.config["CHAIN_SETTINGS"]["ROUTER_2"] = self.ROUTER_2.text()
        self.config["CHAIN_SETTINGS"]["FORK"] = self.FORK.currentIndex()
        self.config["CHAIN_SETTINGS"]["FORK_2"] = self.FORK_2.currentIndex()

        # 没有这个配置选项就跳过
        try:
            self.config["CONFIG"]["EXCHANGE_TARGET"] = self.exchange_target.currentIndex()
        except Exception:
            pass

        try:
            self.config["CHAIN_SETTINGS"]["GAS_STRATEGY"] = self.GAS_STRATEGY.currentIndex()
        except Exception:
            pass

        # MAIN_QUANTITY defaults to auto if you dont fill it.
        quan = self.MAIN_QUANTITY.text()
        if quan == "auto" or len(quan) == 0 or int(quan) <= 0:
            self.config["CONFIG"]["MAIN_QUANTITY"] = "auto"
        else:
            self.config["CONFIG"]["MAIN_QUANTITY"] = int(self.MAIN_QUANTITY.text())

        # VERSION VERIFY
        self.config["CHAIN_SETTINGS"]["VERSION"] = self.FORK.currentText()
        self.config["CHAIN_SETTINGS"]["VERSION_2"] = self.FORK_2.currentText()

        # CLIENT RENAME
        self.name = "{} - chain: {} - account: {}".format(
            self.config["CONFIG"]["SYMBOL"],
            self.config["CHAIN_SETTINGS"]["CHAIN_ID"],
            self.config["CHAIN_SETTINGS"]["MY_ADDRESS"][0:6])
        self.config["NAME"] = self.name
        self.setWindowTitle(self.name)

        # save the file
        with open(self.config_path, 'w', encoding="utf-8") as _:
            json.dump(self.config, _, ensure_ascii=False, indent=1)

        # 内置设置
        stb = is_sturb(self.config["CHAIN_SETTINGS"]["FORK"])
        log.info(f"sturb: {stb}")
        self.config["CHAIN_SETTINGS"]["STURB"] = stb

        return True

    def load(self):
        """Load the config
        Must run this function before save/run
        """
        config_path = QFileDialog.getOpenFileName(self, '选择文件', '', 'Excel files(*.json)')
        self.config_path = str(config_path[0])
        self.config = self.load_parameters(self.config_path)

    def save(self):
        """Save the hand-made config to file, always set the parameter by the way
        Must choose the file path first
        """
        if hasattr(self, "config_path") is False:
            log.info("加载配置后再保存")
            return
        self.set_parameter()
        log.info("Saved")

    def run(self):
        """Run the main loop
        Must load the config first
        """
        if hasattr(self, "config") is False:
            log.info("请预先加载配置")
            return
        if self.loop_is_running:
            log.info("不可同时跑多个")
            return
        self.loop_is_running = True
        self.Logger.clear()
        self.set_parameter()
        self.loop = main_loops(self.config)
        self.loop.start()

    def stop(self):
        """TODO to be killing the thread"""
        if self.loop_is_running is False:
            log.warning("没有程序在运行")
        else:
            log.info("Stopping...")
        # 关闭线程后消灭它
        self.loop.running = False
        self.loop_is_running = False
        self.loop.close()


if __name__ == "__main__":
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    myWin = MyMainForm()
    myWin.show()
    sys.exit(app.exec_())
