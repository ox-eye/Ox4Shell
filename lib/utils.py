import json
import re
from typing import Any, Dict, Tuple, Iterator
from pathlib import Path
import logging
import sys

SIMPLE_PATTERN_REGEX = re.compile(r"(\$\{([^{}]*?)\})")
NESTED_PATTERN_REGEX = re.compile(r"(\$\{(.*)\})")


def find_patterns(text: str) -> Iterator[Tuple[str, str]]:
    for result in SIMPLE_PATTERN_REGEX.findall(text):
        yield result

    for result in NESTED_PATTERN_REGEX.findall(text):
        yield result


def read_mock_data() -> Dict[str, Any]:
    mock_path = Path("mock.json")

    if not mock_path.exists():
        raise Exception(f"Mock file {mock_path} does not exists!")

    with mock_path.open("r") as f:
        data: Dict[str, Any] = json.load(f)
        return data


def setup_logger(logger: logging.Logger) -> None:
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter("%(message)s")
    handler.setFormatter(formatter)

    logger.addHandler(handler)


def set_debug_level(logger: logging.Logger) -> None:
    handler: logging.Handler = logger.handlers[0]

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(filename)s:%(lineno)s at %(funcName)s() - %(levelname)s - %(message)s"
    )
    handler.formatter = formatter
    logger.setLevel(logging.DEBUG)
