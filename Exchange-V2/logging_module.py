import logging


class Event_Logger:
    def __init__(self, level=logging.INFO, filename='example.log', encoding='utf-8'):
        self.logger = logging.getLogger('')
        self.logger.setLevel(level)
        formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        file_handler = logging.FileHandler(filename, mode='w', encoding=encoding)
        file_handler.setFormatter(formatter)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

log = Event_Logger()