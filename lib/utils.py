import re
from typing import Tuple, Iterator
import logging
import sys

# Find simple patterns of ${...}, without any nested occurrences of ${...}
SIMPLE_PATTERN_REGEX = re.compile(r"(\$\{([^{}]*?)\})")

# Find nested patterns of ${...}, where we might find nested ${...} occurrences
NESTED_PATTERN_REGEX = re.compile(r"(\$\{(.*)\})")


def find_patterns(text: str) -> Iterator[Tuple[str, str]]:
    """
    Finds on a given payload pattern according to the logic above
    """
    for result in SIMPLE_PATTERN_REGEX.findall(text):
        yield result

    for result in NESTED_PATTERN_REGEX.findall(text):
        yield result


def setup_logger(logger: logging.Logger) -> None:
    """
    Utility function to set up a logger
    """
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter("%(message)s")
    handler.setFormatter(formatter)

    logger.addHandler(handler)


def set_debug_level(logger: logging.Logger) -> None:
    """
    Utility function to set a logger's level to DEBUG
    """
    handler: logging.Handler = logger.handlers[0]

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(filename)s:%(lineno)s at %(funcName)s() - %(levelname)s - %(message)s"
    )
    handler.formatter = formatter
    logger.setLevel(logging.DEBUG)
