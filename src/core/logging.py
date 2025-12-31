"""
Logging Unifié - Système de logging centralisé
Fusionne core/logging/manager.py
"""
import logging
import sys
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """Formatter avec couleurs pour la console"""
    COLORS = {
        'DEBUG': '\033[36m',
        'INFO': '\033[32m',
        'WARNING': '\033[33m',
        'ERROR': '\033[31m',
        'CRITICAL': '\033[35m',
        'RESET': '\033[0m'
    }

    def format(self, record):
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"
        return super().format(record)


class LogManager:
    """Gestionnaire de logging centralisé"""
    _initialized = False

    @staticmethod
    def init(log_level: str = "INFO"):
        if LogManager._initialized:
            return

        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, log_level.upper()))
        root_logger.handlers = []

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, log_level.upper()))
        console_format = ColoredFormatter(
            '%(levelname)-8s | %(name)-25s | %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_format)
        root_logger.addHandler(console_handler)

        LogManager._initialized = True
        root_logger.info(f"✅ Logging initialisé (niveau: {log_level})")

    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        if not LogManager._initialized:
            LogManager.init()
        return logging.getLogger(name)


def get_logger(name: str) -> logging.Logger:
    """Shortcut pour récupérer un logger"""
    return LogManager.get_logger(name)


# Initialisation auto
LogManager.init()