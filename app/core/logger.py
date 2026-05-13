import logging
import os
from dotenv import load_dotenv

load_dotenv()

def get_logger(name: str = "rocks_ia") -> logging.Logger:
    log_file = os.getenv("ROCKS_LOG_FILE", "logs/rocks_ia.log")

    # Garante que a pasta existe
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    logger = logging.getLogger(name)

    if not logger.handlers:  # Evita duplicar handlers
        logger.setLevel(logging.DEBUG)

        # Handler para arquivo
        fh = logging.FileHandler(log_file, encoding="utf-8")
        fh.setLevel(logging.DEBUG)

        # Handler para console
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        fmt = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s — %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        fh.setFormatter(fmt)
        ch.setFormatter(fmt)

        logger.addHandler(fh)
        logger.addHandler(ch)

    return logger