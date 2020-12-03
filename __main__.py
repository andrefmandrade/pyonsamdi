from logging.config import dictConfig

logging_config = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "detailed": {
            "class": "logging.Formatter",
            "format": "%(asctime)s:%(levelname)s:%(module)s:%(funcName)s:%(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "filters": [],
            "formatter": "detailed",
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": "ultimon.log",
            "mode": "a",
            "formatter": "detailed",
        },
    },
    "loggers": {
        "": {
            "handlers": ["console", "file"], "level": "DEBUG"
        }
    },
}

dictConfig(logging_config)

from settings import DISCORD_TOKEN  # noqa: E402
from disc import run_bot  # noqa: E402

if __name__ == "__main__":
    run_bot(DISCORD_TOKEN)
