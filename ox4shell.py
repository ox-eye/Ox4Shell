from typing import Callable, Dict
from lib.utils import take_one, find_patterns, read_mock_data
from lib.usage import usage
from argparse import ArgumentParser, RawTextHelpFormatter
from pathlib import Path
import logging

logger = logging.getLogger("Ox4Shell")

mock_data_patcher = read_mock_data()


def nop(full_match: str, _: str) -> str:
    return full_match


# Handles the cases of: ${xxx:yyy:zzz:-www}
def str_substitutor_lookup(full_match: str, inner_group: str) -> str:
    parts = inner_group.split(":")
    parts_length = len(parts)
    got_default_value = inner_group.count(":-") > 0

    # no values, return the full match
    if parts_length == 0:
        return full_match

    # single variable
    if parts_length == 1:

        # empty brackets (${})
        if parts[0] == "":
            return ""

        return mock_data_patcher.get(inner_group.lower(), f"<{inner_group.lower()}>")

    # we got some values
    if parts_length > 1:
        # get the default one (last)
        if got_default_value:
            _, _, tail = inner_group.partition(":-")
            return tail
        # no default value provided, return the key
        else:
            return parts[1]

    # unknown
    return full_match


nop_with_default = str_substitutor_lookup

# Handles the cases of: ${lower:aaAAaa}
def str_lower_lookup(_: str, inner_group: str) -> str:
    parts = inner_group.split(":")

    if len(parts) < 2:
        raise Exception("str_lower_lookup must have at least 2 operands!")

    return str(parts[1]).lower()


# Handles the cases of: ${upper:aaAAaa}
def str_upper_lookup(_: str, inner_group: str) -> str:
    parts = inner_group.split(":")

    if len(parts) < 2:
        raise Exception("str_lower_lookup must have at least 2 operands!")

    return str(parts[1]).upper()


# Handles the cases of: ${date:1}
def date_lookup(_: str, inner_group: str) -> str:
    parts = inner_group.split(":")

    if len(parts) != 2:
        raise Exception("date_lookup should have only 2 operands!")

    # the value is wrapped with quotes, so we remove them
    return parts[1][1:-1]


# Handles the cases of: ${env:HOME} for example
def mockable_lookup(full_match: str, inner_group: str) -> str:
    parts = inner_group.split(":")

    if len(parts) < 2:
        raise Exception("mockable_lookup should have at least 2 operands!")

    mock_table_key = parts[0].lower()
    mock_table_value = parts[1].lower()

    mock_value = mock_data_patcher.get(mock_table_key, {}).get(mock_table_value)

    if not mock_value:
        mock_value = str_substitutor_lookup(full_match, inner_group)

    return mock_value


known_lookups: Dict[str, Callable] = {
    "jndi": nop,
    "java": mockable_lookup,
    "sys": mockable_lookup,
    "env": mockable_lookup,
    "os": nop_with_default,
    "lower": str_lower_lookup,
    "upper": str_upper_lookup,
    "date": date_lookup,
}


# handles each result we find
def handle_match(full_match: str, inner_group: str, payload: str) -> str:
    lookup_identifier, *_ = inner_group.split(":")

    logger.debug(f"{full_match=}")
    logger.debug(f"{inner_group=}")
    logger.debug(f"parts: {inner_group.split(':')}")

    normalized_lookup_identifier = str(lookup_identifier).lower()
    logger.debug(f"{normalized_lookup_identifier=}")

    # try to get a handler, if no one found, use the default `str_substitutor_lookup` handler
    func = known_lookups.get(normalized_lookup_identifier, str_substitutor_lookup)
    result = func(full_match, inner_group)

    logger.debug(f"{func.__name__}: {full_match=}, {result=}")
    payload = payload.replace(full_match, result)
    logger.debug("")

    return payload


def deobfuscate_patterns(payload: str) -> str:

    pattern = take_one(find_patterns(payload))

    # if no pattern was found, just return the original payload
    if not pattern:
        return payload

    # if we found a pattern, call the handle match function
    full_match, inner_group = pattern
    payload = handle_match(full_match, inner_group, payload)
    return payload


def deobfuscate(payload: str) -> str:
    are_the_same = False

    while not are_the_same:
        deobfuscated = deobfuscate_patterns(payload)

        if deobfuscated == payload:
            are_the_same = True

        payload = deobfuscated

    return payload


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
        logging.basicConfig(level=logging.DEBUG)

    if args.payload:
        deobfuscated = deobfuscate(args.payload)
        print(deobfuscated)

    if args.file:
        if not args.file.exists():
            print(f"File {args.file} does not exists!")
            exit(1)

        with args.file.open("r") as f:
            for line in f:
                deobfuscated = deobfuscate(line.strip())
                print(deobfuscated)


if __name__ == "__main__":
    main()
