import json
import re
from typing import Any, Dict, Iterable, Optional, Tuple, TypeVar, Iterator

SIMPLE_PATTERN_REGEX = re.compile(r"(\$\{([^{}]*?)\})")
NESTED_PATTERN_REGEX = re.compile(r"(\$\{(.*)\})")

T = TypeVar("T")


def take_one(iterable: Iterable[T]) -> Optional[T]:
    first_item = None

    for item in iterable:
        first_item = item
        break

    return first_item


def find_patterns(text: str) -> Iterator[Tuple[str, str]]:
    for result in SIMPLE_PATTERN_REGEX.findall(text):
        yield result

    for result in NESTED_PATTERN_REGEX.findall(text):
        yield result


def read_mock_data() -> Dict[str, Any]:
    with open("mock.json", "r") as f:
        return json.load(f)
