import json
import time

import requests


def get_gas_price(chain_id):
    try:
        MAX_RETRY = 10
        while MAX_RETRY:
            MAX_RETRY -= 1
            url = f"https://open-api.openocean.finance/v1/{chain_id}/getGasPrice"
            req = requests.get(url=url)
            if req.status_code != 200:
                continue
            dic = json.loads(req.text)
            if "data" not in dic:
                raise Exception(f"chain {chain_id} not supported for openocean gasprice")
            gas_price = dic["data"]["instant"]
            if type(gas_price) is dict:
                return int(int(gas_price["maxFeePerGas"]) * 1.05)
            return int(gas_price * 1.05)
        return None
    except Exception as e:
        print(e)
        time.sleep(1)


if __name__ == '__main__':
    from chain_operation.constants import chain_list
    for i in chain_list.keys():
        print(i, get_gas_price(i))

