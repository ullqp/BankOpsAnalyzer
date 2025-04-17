import logging
import logging.config


def setup_logging():
    logging_config = {
        "version": 1,
        "formatters": {
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO",
                "formatter": "detailed",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            "": {  # root logger
                "handlers": ["console"],
                "level": "INFO",
            },
        },
    }

    logging.config.dictConfig(logging_config)


# Инициализация логгера при импорте модуля
setup_logging()
logger = logging.getLogger(__name__)
