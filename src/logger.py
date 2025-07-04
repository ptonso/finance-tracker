
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from multiprocessing import Pool, cpu_count
import logging

_logger_instance = None

def setup_logging(log_file: Optional[str] = None, level=logging.INFO) -> None:
    """Set up logging configuration."""

    global _logger_instance
    if _logger_instance:
        return

    class CustomFormatter(logging.Formatter):      
        COLORS = {
            'START': '\033[94m',     # Blue
            'ERROR': '\033[91m',     # Red
            'FINISH': '\033[92m',    # Green
            'RESET': '\033[0m',      # Reset to default
        }
        def format(self, record):
            prefix = ''
            if 'START' in record.msg:
                prefix = self.COLORS['START']
            elif 'ERROR' in record.msg:
                prefix = self.COLORS['ERROR']
            elif 'FINISH' in record.msg:
                prefix = self.COLORS['FINISH']

            reset = self.COLORS['RESET']
            self._style._fmt = f'{prefix}%(asctime)s - %(message)s{reset}'
            return super().format(record)
        
    formatter = CustomFormatter()

    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers = []

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(name)s - %(message)s'))
        root_logger.addHandler(file_handler)

    _logger_instance = logging.getLogger("Backup")



class CategoryLogger:
    def __init__(self, category: str = "global"):
        self._category = category
        self._logger = logging.getLogger("Backup")

    def set_category(self, category: str):
        self._category = category

    def _log(self, level, phase, msg, *args, **kwargs):
        prefix = f"[{self._category}] - [{phase}]{' ' * (7 - len(phase))} - "
        self._logger.log(level, prefix + msg, *args, **kwargs)

    def start(self, msg, *args, **kwargs):
        self._log(logging.INFO, "START", msg, *args, **kwargs)

    def finish(self, msg, *args, **kwargs):
        self._log(logging.INFO, "FINISH", msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self._log(logging.INFO, "INFO", msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        self._log(logging.DEBUG, "DEBUG", msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self._log(logging.WARNING, "WARN", msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self._log(logging.ERROR, "ERROR", msg, *args, **kwargs)


def setup_logger(category: str = "global") -> CategoryLogger:
    """Returns a reusable CategoryLogger. Must call setup_logging() once first."""
    return CategoryLogger(category)

