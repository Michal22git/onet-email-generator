import logging
from datetime import datetime

from colorama import Fore, Style


class CustomFormatter(logging.Formatter):
    def format(self, record):
        level_color = Fore.YELLOW
        if record.levelno == logging.DEBUG:
            level_color = Fore.MAGENTA
        elif record.levelno == logging.INFO:
            level_color = Fore.GREEN
        elif record.levelno == logging.WARNING:
            level_color = Fore.YELLOW
        elif record.levelno == logging.ERROR:
            level_color = Fore.RED
        elif record.levelno == logging.CRITICAL:
            level_color = Style.BRIGHT + Fore.RED

        return f"{level_color}[{datetime.now().strftime('%H:%M:%S.%f')}]{super().format(record)}{Style.RESET_ALL}"


class CustomLogger(logging.Logger):
    def __init__(self, name):
        super().__init__(name, level=logging.DEBUG)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(CustomFormatter())
        self.addHandler(console_handler)
