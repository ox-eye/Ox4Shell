import logging
from typing import Callable, Dict

from lib.date_parser import parse_date
from lib.mock import Mock

logger = logging.getLogger("Ox4Shell")
LookupFunction = Callable[[str, str], str]


def handle_single_value(func: LookupFunction) -> LookupFunction:
    """
    Enforces the lookup function to have 2 values.
    If not provided, it will check if it exists as a lookup key.
        If it does, return the full match, since we don't have anything to replace it with.
    If it doesn't - raise an exception
    """

    def wrapper(full_match: str, inner_group: str) -> str:
        if ":" not in inner_group:
            if inner_group in KNOWN_LOOKUPS:
                logger.debug("No variable to lookup, returning full match")
                return full_match

            raise Exception(f"{func.__name__} must contain a ':'!")

        return func(full_match, inner_group)

    return wrapper


def nop_lookup(full_match: str, inner_group: str) -> str:
    """Does nothing other than returning the full match"""
    return full_match


def str_substitutor_lookup(full_match: str, inner_group: str) -> str:
    """
    Handles the cases of: ${xxx:yyy:zzz:-www}, based on:
    https://logging.apache.org/log4j/2.x/log4j-core/apidocs/org/apache/logging/log4j/core/lookup/StrSubstitutor.html
    """
    parts = inner_group.split(":")
    parts_length = len(parts)

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

    logger.debug("Got multiple values")
    # if we got here, we got some values
    # get the default one (last)
    if inner_group.count(":-") > 0:
        logger.debug("Returning default value")
        return inner_group.split(":-", 1)[-1]

    # no default value provided, return the key
    logger.debug("No default value found, returning the full match instead")
    return full_match


@handle_single_value
def str_lower_lookup(full_match: str, inner_group: str) -> str:
    """Handles the cases of: ${lower:aaAAaa}"""
    inner_group = inner_group.split(":-", 1)[0]
    return inner_group.split(":", 1)[1].lower()


@handle_single_value
def str_upper_lookup(full_match: str, inner_group: str) -> str:
    """Handles the cases of: ${upper:aaAAaa}"""
    # ignore default values
    inner_group = inner_group.split(":-", 1)[0]
    return inner_group.split(":", 1)[1].upper()


@handle_single_value
def date_lookup(full_match: str, inner_group: str) -> str:
    """
    Handles the cases of: ${date:1}, ${date:Y}, ${date:Y:-j}
    There are cases where the date formatting in Python is different than the date formatting in Java,
    so minor discrepancies might occur, but the general direction is the same.
    """
    value_group = inner_group.split(":", 1)[1]
    date_values = value_group.split(":-", 1)[0]

    logger.debug(f"Going to parse dates for: {date_values}")

    return parse_date(date_values)


def mockable_lookup(full_match: str, inner_group: str) -> str:
    """Handles the cases of: ${env:HOME} for example"""
    # only key scenario
    if ":" not in inner_group:
        normalized_lookup_id = inner_group.lower()

        # check if the key is in the Mock table
        if normalized_lookup_id in KNOWN_LOOKUPS:
            mock_value = Mock.mock.get(normalized_lookup_id)

            # case where we either didn't find a mock value
            # or the value is the lookup object
            if not mock_value or type(mock_value) != str:
                logger.debug("No variable to lookup, returning full match")
                return full_match

            logger.debug("No variable to lookup, returning mock data")
            return mock_value

        # not in the Mock table, raise exception
        raise Exception("Mockable key not found!")

    # key and value scenario
    parts = inner_group.split(":", 2)

    mock_table_key = parts[0].lower()
    mock_table_value = parts[1].lower()

    mock_value = Mock.mock.get(mock_table_key, {}).get(mock_table_value)
    logger.debug(f"Got mock value of: {mock_value}")

    if not mock_value:
        mock_value = str_substitutor_lookup(full_match, inner_group)

    return str(mock_value)


KNOWN_LOOKUPS: Dict[str, LookupFunction] = {
    "jndi": nop_lookup,
    "os": str_substitutor_lookup,
    "lower": str_lower_lookup,
    "upper": str_upper_lookup,
    "date": date_lookup,
}


def update_lookup_table_with_mock() -> None:
    """Updates the `KNOWN_LOOKUPS` table with values from the `mock.json` file"""
    for key in Mock.mock:
        logger.debug(f"Added a mockable key: {key}")
        KNOWN_LOOKUPS[key] = mockable_lookup


def handle_match(full_match: str, inner_group: str, payload: str) -> str:
    """Handles each result we find"""
    lookup_identifier = inner_group.split(":", 1)[0]

    normalized_lookup_identifier = lookup_identifier.lower()
    logger.debug(f"Looking up the callback for: {normalized_lookup_identifier=}")

    # try to get a handler, if no one found, use the default `str_substitutor_lookup` handler
    func = KNOWN_LOOKUPS.get(normalized_lookup_identifier, str_substitutor_lookup)
    logger.debug(f"Selected lookup function is {func.__name__}")
    result = func(full_match, inner_group)

    logger.debug(f"Executed callback: {func.__name__}({full_match=}, {result=})\n")
    payload = payload.replace(full_match, result)

    return payload
