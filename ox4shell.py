from typing import Callable, Dict
from lib.utils import find_patterns, read_mock_data, set_debug_level
from lib.usage import usage
from argparse import ArgumentParser, RawTextHelpFormatter
from pathlib import Path
import logging
import sys

logger = logging.getLogger("Ox4Shell")
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter("%(message)s")
handler.setFormatter(formatter)

logger.addHandler(handler)


mock_data = read_mock_data()
MAX_DEPTH = 150


def nop(full_match: str, _: str) -> str:
    return full_match


# Handles the cases of: ${xxx:yyy:zzz:-www}
def str_substitutor_lookup(full_match: str, inner_group: str) -> str:
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

        return mock_data.get(inner_group.lower(), f"<{inner_group.lower()}>")

    # if we got here, we got some values
    # get the default one (last)
    if inner_group.count(":-") > 0:
        return inner_group.split(":-", 1)[-1]

    # no default value provided, return the key
    return parts[1]


nop_with_default = str_substitutor_lookup

# Handles the cases of: ${lower:aaAAaa}
def str_lower_lookup(_: str, inner_group: str) -> str:
    if inner_group.count(":") < 2:
        raise Exception("str_lower_lookup must have at least 2 operands!")

    return inner_group.split(":", 1)[1].lower()


# Handles the cases of: ${upper:aaAAaa}
def str_upper_lookup(_: str, inner_group: str) -> str:
    if inner_group.count(":") < 2:
        raise Exception("str_upper_lookup must have at least 2 operands!")

    return inner_group.split(":", 1)[1].upper()


# Handles the cases of: ${date:1}
def date_lookup(_: str, inner_group: str) -> str:
    if inner_group.count(":") < 2:
        raise Exception("date_lookup must have at least 2 operands!")

    # the value is wrapped with quotes, so we remove them
    return inner_group.split(":", 1)[1][1:-1]


# Handles the cases of: ${env:HOME} for example
def mockable_lookup(full_match: str, inner_group: str) -> str:
    if inner_group.count(":") < 2:
        raise Exception("mockable_lookup should have at least 2 operands!")

    parts = inner_group.split(":", 2)

    mock_table_key = parts[0].lower()
    mock_table_value = parts[1].lower()

    mock_value: str = mock_data.get(mock_table_key, {}).get(mock_table_value)

    if not mock_value:
        mock_value = str_substitutor_lookup(full_match, inner_group)

    return mock_value


KNOWN_LOOKUPS: Dict[str, Callable[[str, str], str]] = {
    "jndi": nop,
    "java": mockable_lookup,
    "sys": mockable_lookup,
    "env": mockable_lookup,
    "os": nop_with_default,
    "lower": str_lower_lookup,
    "upper": str_upper_lookup,
    "date": date_lookup,
}


# ${jndi:ldap://aa/a}
# ${jndi:ldap://aa/a} , jndi:ldap://aa/a

# handles each result we find
def handle_match(full_match: str, inner_group: str, payload: str) -> str:
    lookup_identifier = inner_group.split(":", 1)[0]

    normalized_lookup_identifier = str(lookup_identifier).lower()
    logger.debug(f"Looking up the callback for: {normalized_lookup_identifier=}")

    # try to get a handler, if no one found, use the default `str_substitutor_lookup` handler
    func = KNOWN_LOOKUPS.get(normalized_lookup_identifier, str_substitutor_lookup)
    result = func(full_match, inner_group)

    logger.debug(f"Executing callback: {func.__name__}({full_match=}, {result=})\n")
    payload = payload.replace(full_match, result)

    return payload


def deobfuscate_patterns(payload: str) -> str:
    pattern = next(find_patterns(payload), None)

    # if no pattern was found, just return the original payload
    if not pattern:
        return payload

    # if we found a pattern, call the handle match function
    full_match, inner_group = pattern

    logger.debug("Found full text to replace: ${full_match}")
    logger.debug("Found text to lookup by: ${inner_group}")

    payload = handle_match(full_match, inner_group, payload)
    return payload


def deobfuscate(payload: str) -> str:
    for _ in range(MAX_DEPTH):
        deobfuscated = deobfuscate_patterns(payload)

        if deobfuscated == payload:
            return deobfuscated

        payload = deobfuscated

    raise Exception(f"deobfuscate exceeded max depth of {MAX_DEPTH}")


def main() -> None:
    parser = ArgumentParser(
        prog="ox4shell", description=usage, formatter_class=RawTextHelpFormatter
    )
    parser.add_argument(
        "-d", "--debug", default=False, help="Enable debug mode", action="store_true"
    )

    target_group = parser.add_mutually_exclusive_group(required=True)
    target_group.add_argument(
        "-p", "--payload", type=str, help="The payload to deobfuscate"
    )
    target_group.add_argument(
        "-f", "--file", type=Path, help="A file containing payloads"
    )

    args = parser.parse_args()

    if args.debug:
        set_debug_level(logger)

    if args.payload:
        deobfuscated = deobfuscate(args.payload)
        logger.info(deobfuscated)

    if args.file:
        if not args.file.exists():
            raise Exception(f"File {args.file} does not exists!")

        with args.file.open("r") as f:
            for line in f:
                deobfuscated = deobfuscate(line.strip())
                print(deobfuscated)


if __name__ == "__main__":
    main()
