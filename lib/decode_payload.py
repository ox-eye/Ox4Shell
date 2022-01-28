import binascii
import re
from typing import Optional, List
from urllib.parse import urlparse
import base64

from logging import getLogger
logger = getLogger("Ox4Shell")

# Extracts the an JNDI Log4j tag content from a tag with the form of:
# ${jndi:ldap://<CONTENT>}
INTERNAL_TAG_REGEX = re.compile(r"\$\{jndi:ldap://(.*?)(?:\:\-.*?)?\}")

# Extracts the command content from the full path
EXTRACT_COMMAND_REGEX = re.compile(r"\/Basic\/Command\/Base64\/(.*?)$")


def safe_b64_decode(string: str) -> Optional[str]:
    try:
        return base64.b64decode(string, validate=True).decode()
    except binascii.Error:
        logger.debug(f"Failed base64 decoding {string=}")
        return None


def base64_decode_payload(payload: str) -> str:
    tags: List[str] = INTERNAL_TAG_REGEX.findall(payload)

    if not tags:
        logger.debug(f"Can't find proper tags within the {payload=}")
        return payload

    path = urlparse(tags[0]).path
    commands: List[str] = EXTRACT_COMMAND_REGEX.findall(path)

    if not commands:
        logger.debug(f"can't find commands within the {path=}")
        return payload

    command = commands[0]
    decoded = safe_b64_decode(command)

    if not decoded:
        logger.debug(f"Can't decode command {command=}")
        return payload

    changed_payload = payload.replace(command, decoded)
    return changed_payload
