
import json
import time

from chain_operation.chain_utils import chain_utils
from exchange_operation.the_binance_client import binance_client


if __name__ == "__main__":
    # 加载Cypress pangea test.json配置
    with open("Arb test.json", "r", encoding='utf8') as f:
        config = json.load(f)
    test = chain_utils(config)
    print("chain init complete")
    nonce = test.get_nonce()
    print("nonce init complete")
    gas_price = config["CHAIN_SETTINGS"]["GAS_PRICE"] * 10 ** 9
    # binance_test = binance_client(config)
    # print("binance init complete")

    # fake_price = binance_test.get_ticker_price()
    fake_price = 1.24
    data = {
        "gas_price": gas_price,
        "nonce": nonce,
        "sell_pred": fake_price,
        "buy_pred": fake_price,
    }
    # start to test
    print("init completes, test starts.")
    print("==" * 20)

    # binance_test.marked_order(
    #     side="BUY",
    #     quantity=1
    # )
    # while True:
    #     print(test.get_price(100, data))
    #     time.sleep(3)

    # 0买,1卖
    test.send_transaction(0, 0.001, data, False)