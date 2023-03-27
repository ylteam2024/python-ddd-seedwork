import logging
from traceback import print_exception

from .AbstractLogger import AbstractLogger

LOG_FORMAT = (
    "%(levelname) -10s %(asctime)s %(name) -30s %(funcName) "
    "-35s %(lineno) -5d: %(message)s"
)

SIMPLE_LOGGER = logging.getLogger(__name__)


class DomainLogger(AbstractLogger):
    def info(self, message: str):
        SIMPLE_LOGGER.info(f"[{self.tag()}] {message}")

    def error(self, message: str, error: Exception | None = None):
        SIMPLE_LOGGER.error(f"[{self.tag()}] {message} f{print_exception(error)}")

    def exception(self, error: Exception | None = None):
        SIMPLE_LOGGER.error(f"[{self.tag()}] f{print_exception(error)}")

    def warning(self, message: str):
        SIMPLE_LOGGER.warning(f"[{self.tag()}] {message}")
