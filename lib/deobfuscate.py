from lib.utils import find_patterns
from lib.lookups import handle_match, update_lookup_table_with_mock
from lib.decode_payload import base64_decode_payload
import logging

logger = logging.getLogger("Ox4Shell")

DEFAULT_MAX_DEPTH = 150


def deobfuscate_patterns(payload: str) -> str:
    """
    An internal deobfuscation pattern that operates on a given payload by the researched patterns:
        - `lib/utils.py:SIMPLE_PATTERN_REGEX`
        - `lib/utils.py:NESTED_PATTERN_REGEX`
    """
    pattern = next(find_patterns(payload), None)
    logger.debug(f"Got deobfuscation pattern - {pattern}")

    # if no pattern was found, just return the original payload
    if not pattern:
        logger.debug("Pattern is empty, returning original payload")
        return payload

    # if we found a pattern, call the handle match function
    full_match, inner_group = pattern

    logger.debug(f"Found full text to replace: {full_match=}")
    logger.debug(f"Found text to lookup by: {inner_group=}")

    payload = handle_match(full_match, inner_group, payload)
    return payload


def deobfuscate(payload: str, max_depth: int = DEFAULT_MAX_DEPTH, decode_base64: bool = False) -> str:
    """
    The public method to deobfuscates a payload.
    """
    update_lookup_table_with_mock()

    for i in range(max_depth):
        logger.debug(f"Entering iteration #{i}")
        logger.debug(f"Trying to deobfuscate {payload}")

        deobfuscated = deobfuscate_patterns(payload)
        logger.debug(f"Deobfuscated result is: {deobfuscated}")

        if deobfuscated == payload:
            logger.debug("Payload equals deobfuscated, exiting loop")
            if decode_base64:
                return base64_decode_payload(deobfuscated)

            return deobfuscated

        payload = deobfuscated

    raise Exception(f"deobfuscate exceeded max depth of {max_depth}")
