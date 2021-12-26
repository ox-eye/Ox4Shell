import logging
from typing import Callable, Dict

from lib.date_parser import parse_date
from lib.mock import Mock

logger = logging.getLogger("Ox4Shell")


def nop_lookup(full_match: str, inner_group: str) -> str:
    return full_match


# Handles the cases of: ${xxx:yyy:zzz:-www}
def str_substitutor_lookup(full_match: str, inner_group: str) -> str:
    parts = inner_group.split(":")
    parts_length = len(parts)

    logger.debug(f"{parts=}")

    # no values, return the full match
    if parts_length == 0:
        logger.debug("No values found, returning full match")
        return full_match

    # single variable
    if parts_length == 1:
        logger.debug("Got a single variable back")

        # empty brackets (${})
        if parts[0] == "":
            logger.debug("Found empty brackets")
            return ""

        logger.debug("Not empty, so returning full match")
        return full_match

        # logger.debug("Returning mock value")
        # return Mock.mock.get(inner_group.lower(), f"<{inner_group.lower()}>")

    logger.debug("Got multiple values")
    # if we got here, we got some values
    # get the default one (last)
    if inner_group.count(":-") > 0:
        logger.debug("Returning default value")
        return inner_group.split(":-", 1)[-1]

    # no default value provided, return the key
    logger.debug("No default value found, returning the full match instead")
    return full_match


# Handles the cases of: ${lower:aaAAaa}
def str_lower_lookup(full_match: str, inner_group: str) -> str:
    if ":" not in inner_group:
        if inner_group in KNOWN_LOOKUPS.keys():
            logger.debug("No variable to lookup, returning full match")
            return full_match

        raise Exception("str_lower_lookup must contain a ':'!")

    # ignore default values
    inner_group = inner_group.split(":-", 1)[0]

    return inner_group.split(":", 1)[1].lower()


# Handles the cases of: ${upper:aaAAaa}
def str_upper_lookup(full_match: str, inner_group: str) -> str:
    if ":" not in inner_group:
        if inner_group in KNOWN_LOOKUPS.keys():
            logger.debug("No variable to lookup, returning full match")
            return full_match

        raise Exception("str_upper_lookup must contain a ':'!")

    # ignore default values
    inner_group = inner_group.split(":-", 1)[0]

    return inner_group.split(":", 1)[1].upper()


# Handles the cases of: ${date:1}, ${date:Y}, ${date:Y:-j}
# There are cases where the date formatting in Python is different
# than the date formatting in Java, so minor discrepancies might
# occur, but the general direction is the same
def date_lookup(full_match: str, inner_group: str) -> str:
    if ":" not in inner_group:
        if inner_group in KNOWN_LOOKUPS.keys():
            logger.debug("No variable to lookup, returning full match")
            return full_match

        raise Exception("date_lookup must contain a ':'!")

    value_group = inner_group.split(":", 1)[1]
    date_values = value_group.split(":-", 1)[0]

    logger.debug(f"Going to parse dates for: {date_values}")

    return parse_date(date_values)


# Handles the cases of: ${env:HOME} for example
def mockable_lookup(full_match: str, inner_group: str) -> str:
    if ":" not in inner_group:
        if inner_group in KNOWN_LOOKUPS.keys():
            logger.debug("No variable to lookup, returning full match")
            return full_match

        raise Exception("mockable_lookup must contain a ':'!")

    parts = inner_group.split(":", 2)

    mock_table_key = parts[0].lower()
    mock_table_value = parts[1].lower()

    mock_value: str = Mock.mock.get(mock_table_key, {}).get(mock_table_value)
    logger.debug(f"Got mock value of: {mock_value}")

    if not mock_value:
        mock_value = str_substitutor_lookup(full_match, inner_group)

    return mock_value


KNOWN_LOOKUPS: Dict[str, Callable[[str, str], str]] = {
    "jndi": nop_lookup,
    "os": str_substitutor_lookup,
    "lower": str_lower_lookup,
    "upper": str_upper_lookup,
    "date": date_lookup,
}


def update_lookup_table():
    for key in Mock.mock.keys():
        logger.debug(f"Added a mockable key: {key}")
        KNOWN_LOOKUPS[key] = mockable_lookup


# ${jndi:ldap://aa/a}
# ${jndi:ldap://aa/a}, jndi:ldap://aa/a
# handles each result we find
def handle_match(full_match: str, inner_group: str, payload: str) -> str:
    lookup_identifier = inner_group.split(":", 1)[0]

    normalized_lookup_identifier = str(lookup_identifier).lower()
    logger.debug(f"Looking up the callback for: {normalized_lookup_identifier=}")

    # try to get a handler, if no one found, use the default `str_substitutor_lookup` handler
    func = KNOWN_LOOKUPS.get(normalized_lookup_identifier, str_substitutor_lookup)
    logger.debug(f"Selected lookup function is {func.__name__}")
    result = func(full_match, inner_group)

    logger.debug(f"Executed callback: {func.__name__}({full_match=}, {result=})\n")
    payload = payload.replace(full_match, result)

    return payload
