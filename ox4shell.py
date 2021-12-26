from lib.utils import setup_logger, set_debug_level
from lib.usage import usage
from lib.deobfuscate import deobfuscate
from lib.mock import Mock
from argparse import ArgumentParser, RawTextHelpFormatter
from pathlib import Path
import logging

logger = logging.getLogger("Ox4Shell")
setup_logger(logger)


def main() -> None:
    parser = ArgumentParser(
        prog="ox4shell", description=usage, formatter_class=RawTextHelpFormatter
    )
    parser.add_argument(
        "-d", "--debug", default=False, help="Enable debug mode", action="store_true"
    )

    parser.add_argument(
        "-m",
        "--mock",
        default=Path("mock.json"),
        help="The location of the mock data JSON file that replaces certain values in the payload",
        type=Path,
    )

    target_group = parser.add_mutually_exclusive_group(required=True)
    target_group.add_argument(
        "-p", "--payload", type=str, help="A single payload to deobfuscate, make sure to escape '$' signs"
    )
    target_group.add_argument(
        "-f", "--file", type=Path, help="A file containing payloads (delimited by newline)"
    )

    args = parser.parse_args()

    if args.debug:
        set_debug_level(logger)

    logger.debug(f"Using mock file: {args.mock}")
    Mock.populate(args.mock)

    if args.payload:
        deobfuscated = deobfuscate(args.payload)
        logger.info(deobfuscated)

    elif args.file:
        if not args.file.exists():
            raise Exception(f"File {args.file} does not exists!")

        with args.file.open("r") as f:
            for line in f:
                deobfuscated = deobfuscate(line.strip())
                logger.info(deobfuscated)


if __name__ == "__main__":
    main()
