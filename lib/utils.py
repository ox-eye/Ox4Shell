import re

SIMPLE_PATTERN_REGEX = re.compile(r"(\$\{([^{}]*?)\})")
NESTED_PATTERN_REGEX = re.compile(r"(\$\{(.*)\})")


def take_one(iterable):
    for item in iterable:
        return item


def find_patterns(text):
    for result in SIMPLE_PATTERN_REGEX.findall(text):
        yield result

    for result in NESTED_PATTERN_REGEX.findall(text):
        yield result
