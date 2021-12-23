import json
import re
from typing import Any, Dict, Tuple, Iterator
from pathlib import Path
import logging

SIMPLE_PATTERN_REGEX = re.compile(r"(\$\{([^{}]*?)\})")
NESTED_PATTERN_REGEX = re.compile(r"(\$\{(.*)\})")


def find_patterns(text: str) -> Iterator[Tuple[str, str]]:
    for result in SIMPLE_PATTERN_REGEX.findall(text):
        yield result

    for result in NESTED_PATTERN_REGEX.findall(text):
        yield result


def read_mock_data() -> Dict[str, Any]:
    p = Path("mock.json")

    if not p.exists():
        raise Exception(f"Mock file {p} does not exists!")

    with p.open("r") as f:
        data: Dict[str, Any] = json.load(f)
        return data


def set_debug_level(logger: logging.Logger) -> None:
    handler: logging.Handler = logger.handlers[0]

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.formatter = formatter
    handler.setLevel(logging.DEBUG)
