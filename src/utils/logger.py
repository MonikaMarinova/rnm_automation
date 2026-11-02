"""Logger factory. Handlers/levels are configured by pytest (see pytest.ini)."""
import logging


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(f"rm.{name}")