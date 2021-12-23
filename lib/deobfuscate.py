from lib.utils import read_mock_data, find_patterns
from lib.lookups import handle_match
import logging

logger = logging.getLogger("Ox4Shell")

mock = read_mock_data()
MAX_DEPTH = 150


def deobfuscate_patterns(payload: str) -> str:
    pattern = next(find_patterns(payload), None)

    # if no pattern was found, just return the original payload
    if not pattern:
        return payload

    # if we found a pattern, call the handle match function
    full_match, inner_group = pattern

    logger.debug("Found full text to replace: ${full_match}")
    logger.debug("Found text to lookup by: ${inner_group}")

    payload = handle_match(mock, full_match, inner_group, payload)
    return payload


def deobfuscate(payload: str) -> str:
    for _ in range(MAX_DEPTH):
        deobfuscated = deobfuscate_patterns(payload)

        if deobfuscated == payload:
            return deobfuscated

        payload = deobfuscated

    raise Exception(f"deobfuscate exceeded max depth of {MAX_DEPTH}")
