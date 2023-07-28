"""
这玩意儿主要是拿来作异常控制结构
但是具体异常的处理放入errors.py
"""
import time

from binance.error import ClientError

from errors import binance_error_handler, connection_error_handler


def off_chain_exception_handler(func):
    """
    捕获，通过errors排错
    """
    def wrapper(*args, **kwargs):
        while True:
            try:
                return func(*args, **kwargs)
            except ClientError as e:
                binance_error_handler(e, func.__name__)
                time.sleep(3)
            except Exception as e:
                connection_error_handler(e, func.__name__)
                time.sleep(3)

    return wrapper