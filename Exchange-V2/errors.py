"""
2022/10/17
GENERAL HANDLERS
"""
import time

from binance.error import ClientError
from requests.exceptions import ProxyError, SSLError
from logging_module import log


def binance_error_handler(e: ClientError, func_name: str):
    """binance error handler
    CAN ONLY BE USED WHEN BINANCE OPERATES
    WHEN USE, CONSIDER HANDLE OTHER EXCEPTIONS AFTERWARDS
    ACCESSES(retry):
        -1021: timestamp is out of recvWindow
        -1001: internal error
        -1003: requests overloads, wait 10s
    DENIES(raise exception):
        -4004: quantity too low(lower than 5 dollars)
        -1111: ...
    """
    if type(e) is not ClientError:
        log.error("e is not a client error, dev:注意except的错误类型，并且检查以下的func_name")
        log.error("error msg: {}, func_name: {}".format(e.args, func_name))
        return 0
    code = e.error_code
    if code == -1021:  # ACC
        log.warning("时间戳错误，可能是网络波动，或者请尝试同步本地时间")
    elif code == -4004:  # DEN
        raise Exception("计算得到的币安交易量不符合精度。建议确认CONFIG PRECISE是否过 小")
    elif code == -1111:  # DEN
        raise Exception("计算得到的币安交易量不符合精度。建议确认CONFIG PRECISE是否过 大")
    elif code == -1001:  # ACC
        log.warning("DISCONNECTED, 内部错误; 无法处理您的请求，币安服务器错误居多，重试")
    elif code == -1003:  # ACC but mes
        log.warning("TOO MANY REQUESTS, 单终端请求负载过多, 原因如下：")
        log.warning(e.args)
        time.sleep(10)
    elif code == -1121:  # DEN
        raise Exception(e)
    else:  # DEN
        log.error("不属于已处理的任何币安错误，请联系我并且记得截图log")
        raise e


def connection_error_handler(e, func_name):
    """
    connection error handler
    including:
    requests.exceptions.ProxyError: access
    ...
    """
    try:
        raise e
    except ProxyError:
        log.error("Proxy Error, retrying...  检查你的连接，以及代理")
    except SSLError:
        log.error("SSLError, retrying...")
    except Exception as e:
        log.error(type(e))
        log.error("other errors: {}, func_name: {}".format(e.args, func_name))  # 注意此处全部放行，但是理论上存在异常不可放行
        # raise any e?