import logging
from typing import Any, Callable, Dict

logger = logging.getLogger("Ox4Shell")

MockData = Dict[str, Any]


def nop_lookup(mock: MockData, full_match: str, inner_group: str) -> str:
    return full_match


# Handles the cases of: ${xxx:yyy:zzz:-www}
def str_substitutor_lookup(mock: MockData, full_match: str, inner_group: str) -> str:
    parts = inner_group.split(":")
    parts_length = len(parts)

    # no values, return the full match
    if parts_length == 0:
        return full_match

    # single variable
    if parts_length == 1:

        # empty brackets (${})
        if parts[0] == "":
            return ""

        return mock.get(inner_group.lower(), f"<{inner_group.lower()}>")

    # if we got here, we got some values
    # get the default one (last)
    if inner_group.count(":-") > 0:
        return inner_group.split(":-", 1)[-1]

    # no default value provided, return the key
    return parts[1]


# Handles the cases of: ${lower:aaAAaa}
def str_lower_lookup(mock: MockData, full_match: str, inner_group: str) -> str:
    if ":" not in inner_group:
        raise Exception("str_lower_lookup must contain a ':'!")

    return inner_group.split(":", 1)[1].lower()


# Handles the cases of: ${upper:aaAAaa}
def str_upper_lookup(mock: MockData, full_match: str, inner_group: str) -> str:
    if ":" not in inner_group:
        raise Exception("str_upper_lookup must contain a ':'!")

    return inner_group.split(":", 1)[1].upper()


# Handles the cases of: ${date:1}
def date_lookup(mock: MockData, full_match: str, inner_group: str) -> str:
    if ":" not in inner_group:
        raise Exception("date_lookup must contain a ':'!")

    # the value is wrapped with quotes, so we remove them
    return inner_group.split(":", 1)[1][1:-1]


# Handles the cases of: ${env:HOME} for example
def mockable_lookup(mock: MockData, full_match: str, inner_group: str) -> str:
    if ":" not in inner_group:
        raise Exception("mockable_lookup must contain a ':'!")

    parts = inner_group.split(":", 2)

    mock_table_key = parts[0].lower()
    mock_table_value = parts[1].lower()

    mock_value: str = mock.get(mock_table_key, {}).get(mock_table_value)

    if not mock_value:
        mock_value = str_substitutor_lookup(mock, full_match, inner_group)

    return mock_value


KNOWN_LOOKUPS: Dict[str, Callable[[MockData, str, str], str]] = {
    "jndi": nop_lookup,
    "java": mockable_lookup,
    "sys": mockable_lookup,
    "env": mockable_lookup,
    "os": str_substitutor_lookup,
    "lower": str_lower_lookup,
    "upper": str_upper_lookup,
    "date": date_lookup,
}


# ${jndi:ldap://aa/a}
# ${jndi:ldap://aa/a} , jndi:ldap://aa/a
# handles each result we find
def handle_match(
    mock: MockData, full_match: str, inner_group: str, payload: str
) -> str:
    lookup_identifier = inner_group.split(":", 1)[0]

    normalized_lookup_identifier = str(lookup_identifier).lower()
    logger.debug(f"Looking up the callback for: {normalized_lookup_identifier=}")

    # try to get a handler, if no one found, use the default `str_substitutor_lookup` handler
    func = KNOWN_LOOKUPS.get(normalized_lookup_identifier, str_substitutor_lookup)
    result = func(mock, full_match, inner_group)

    logger.debug(f"Executing callback: {func.__name__}({full_match=}, {result=})\n")
    payload = payload.replace(full_match, result)

    return payload
