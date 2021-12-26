from datetime import datetime
from itertools import groupby
from typing import Callable, Dict, List
from math import ceil, floor
from logging import getLogger

logger = getLogger("Ox4Shell")

# Adjusted from the Java docs - https://docs.oracle.com/javase/6/docs/api/java/text/SimpleDateFormat.html


def left_pad_with_zeros(text: str, zeros_count: int) -> str:
    return (zeros_count * "0") + text


def parse_text(now: datetime, key: str, group: List[str]) -> str:
    # Era designator
    if key == "G":
        # no length implications
        return "AD"

    # Day in week
    if key == "E":
        # full form
        if len(group) >= 4:
            return now.strftime("%A")

        # abbreviated form
        return now.strftime("%a")

    # Am/pm marker
    if key == "a":
        # no length implications
        return now.strftime("%p")

    raise Exception(f"Unknown character {key} for parse_text")


def parse_year(now: datetime, key: str, group: List[str]) -> str:
    # TODO: capital Y should have a special care, for now treat as the same
    if key not in ["y", "Y"]:
        raise Exception(f"Unknown character {key} for parse_year")

    group_length = len(group)

    if group_length == 2:
        return now.strftime("%y")

    formatted_now = now.strftime("%Y")
    padding = group_length - len(formatted_now)

    return left_pad_with_zeros(formatted_now, padding)


def parse_month(now: datetime, key: str, group: List[str]) -> str:
    if key != "M":
        raise Exception(f"Unknown character {key} for parse_month")

    group_length = len(group)

    # Month as a zero-padded decimal number (01, 02, …, 12)
    if group_length <= 2:
        return now.strftime("%m")

    # Month as locale’s abbreviated name (Jan, Feb, …)
    if group_length == 3:
        return now.strftime("%b")

    # Month as locale’s full name.
    return now.strftime("%B")


def parse_number(now: datetime, key: str, group: List[str]) -> str:
    formatted_now = None

    # Week in year
    if key == "w":
        formatted_now = now.strftime("%U").lstrip("0") or "0"

    # Week in month
    if key == "W":
        first_day = now.replace(day=2)
        dom = now.day + first_day.weekday()
        formatted_now = str(int(ceil(dom / 7.0)))

    # Day in year
    if key == "D":
        formatted_now = now.strftime("%j").lstrip("0") or "0"

    # Day in month
    if key == "d":
        formatted_now = now.strftime("%d").lstrip("0") or "0"

    # Day of week in month
    if key == "F":
        day_in_month = int(now.strftime("%d").lstrip("0"))
        formatted_now = str(ceil(day_in_month / 7))

    # Hour in day (0-23)
    if key == "H":
        formatted_now = now.strftime("%H").lstrip("0") or "0"

    # Hour in day (1-24)
    if key == "k":
        hours = int(now.strftime("%H").lstrip("0") or "0")  # this gives 0-23
        formatted_now = str(hours + 1)

    # Hour in am/pm (0-11)
    if key == "K":
        hours = int(now.strftime("%I").lstrip("0") or "0")  # this gives 1-12
        formatted_now = str(hours - 1)

    # Hour in am/pm (1-12)
    if key == "h":
        formatted_now = now.strftime("%I").lstrip("0")

    # Minute in hour
    if key == "m":
        formatted_now = now.strftime("%M").lstrip("0")

    # Second in minute
    if key == "s":
        formatted_now = now.strftime("%S").lstrip("0")

    # Millisecond
    if key == "S":
        microseconds = int(now.strftime("%f").lstrip("0") or "0")
        formatted_now = str(floor(microseconds / 1_000))

    if formatted_now:
        padding = len(group) - len(formatted_now)
        return left_pad_with_zeros(formatted_now, padding)

    raise Exception(f"Unknown character {key} for parse_number")


def parse_general_timezone(now: datetime, key: str, group: List[str]) -> str:
    # currently only mocking data, not reason to
    # reveal the true timezone in the payload
    if key != "z":
        raise Exception(f"Unknown character {key} for parse_general_timezone")

    if len(group) < 4:
        return "GMT"

    return "Greenwich Mean Time"


def parse_rfc_822_timezone(now: datetime, key: str, group: List[str]) -> str:
    # currently only mocking data, not reason to
    # reveal the true timezone in the payload
    if key != "Z":
        raise Exception(f"Unknown character {key} for parse_rfc_822_timezone")

    return "+0000"


def parse_noop(now: datetime, key: str, group: List[str]) -> str:
    if key == " ":
        return " " * len(group)

    return "".join(group)


ParseFunc = Callable[[datetime, str, List[str]], str]

mapping: Dict[str, ParseFunc] = {
    "G": parse_text,
    "y": parse_year,
    "Y": parse_year,
    "M": parse_month,
    "w": parse_number,
    "W": parse_number,
    "D": parse_number,
    "d": parse_number,
    "F": parse_number,
    "E": parse_text,
    "a": parse_text,
    "H": parse_number,
    "k": parse_number,
    "K": parse_number,
    "h": parse_number,
    "m": parse_number,
    "s": parse_number,
    "S": parse_number,
    "z": parse_general_timezone,
    "Z": parse_rfc_822_timezone,
}


def parse_date(date_text: str) -> str:
    parts: List[str] = []
    now = datetime.now()
    logger.debug(f"Parsing date according to: {now=}")

    for key, group in groupby(date_text):
        consumed_group = list(group)
        func = mapping.get(key, parse_noop)
        logger.debug(
            f"Executing parsing func: {func.__name__}({key}, {consumed_group})"
        )

        result = func(now, key, consumed_group)
        logger.debug(f"Got back: {result=}")

        parts.append(result)

    return "".join(parts)
