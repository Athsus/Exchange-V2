import logging
import time
import traceback

from requests.exceptions import ProxyError
from _utils.log import log


def chain_exception_catcher(func):
    """
    对于信息获取，总是重试，并且报告是任何类型的错误
    可扩展
    """
    def wrapper(*args, **kwargs):
        while True:
            try:
                return func(*args, **kwargs)
            except ProxyError as e:
                log.info("Proxy Error, ...")
                time.sleep(3)
                continue
            except Exception as e:
                log.warning(traceback.format_exc())
                time.sleep(3)
                continue

    return wrapper


def transaction_exception_handler(func):
    """
    对于transaction的错误处理
    任何错误应该报告，丢出去，并且停止
    """

    def wrapper(*args, **kwargs):
        while True:
            try:
                ret = func(*args, **kwargs)
                log.info("Transaction complete")
                return ret
            except Exception as e:
                log.warning(f"transaction failed for exception: {e}")
                return None

    return wrapper