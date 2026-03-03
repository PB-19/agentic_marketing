import logging
from pathlib import Path

_LOG_FILE = Path(__file__).resolve().parent / "logs" / "app.log"


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        fmt = logging.Formatter(
            "%(asctime)s [%(levelname)s] [%(filename)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        stream = logging.StreamHandler()
        stream.setFormatter(fmt)

        _LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(_LOG_FILE, encoding="utf-8")
        file_handler.setFormatter(fmt)

        logger.addHandler(stream)
        logger.addHandler(file_handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False
    return logger
