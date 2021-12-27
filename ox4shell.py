from lib.utils import setup_logger, set_debug_level
from lib.usage import usage
from lib.deobfuscate import deobfuscate, DEFAULT_MAX_DEPTH
from lib.mock import Mock
from argparse import ArgumentParser, RawTextHelpFormatter, ArgumentDefaultsHelpFormatter
from pathlib import Path
import logging

logger = logging.getLogger("Ox4Shell")
setup_logger(logger)


class CustomArgumentFormatter(ArgumentDefaultsHelpFormatter, RawTextHelpFormatter):
    ...


def main() -> None:
    parser = ArgumentParser(
        prog="ox4shell",
        description=usage,
        formatter_class=CustomArgumentFormatter,
        add_help=False,
    )

    general_group = parser.add_argument_group(title="General")
    general_group.add_argument(
        "-h", "--help", action="help", help="show this help message and exit"
    )
    general_group.add_argument(
        "-d", "--debug", default=False, help="Enable debug mode", action="store_true"
    )

    general_group.add_argument(
        "-m",
        "--mock",
        default=Path("mock.json"),
        help="The location of the mock data JSON file that replaces certain values in the payload",
        type=Path,
    )

    general_group.add_argument(
        "--max-depth",
        default=DEFAULT_MAX_DEPTH,
        help="The maximum number of iteration to perform on a given payload",
        type=int,
    )

    target_group = parser.add_argument_group(
        title="Targets", description="Choose which target payloads to run Ox4Shell on"
    )
    target_mutex_group = target_group.add_mutually_exclusive_group(required=True)

    target_mutex_group.add_argument(
        "-p",
        "--payload",
        type=str,
        help="A single payload to deobfuscate, make sure to escape '$' signs",
    )
    target_mutex_group.add_argument(
        "-f",
        "--file",
        type=Path,
        help="A file containing payloads delimited by newline",
    )

    args = parser.parse_args()

    if args.debug:
        set_debug_level(logger)

    logger.debug(f"Using mock file: {args.mock}")
    Mock.populate(args.mock)

    if args.payload:
        deobfuscated = deobfuscate(args.payload, max_depth=args.max_depth)
        logger.info(deobfuscated)

    if args.file:
        if not args.file.exists():
            raise Exception(f"File {args.file} does not exists!")

        with args.file.open("r") as f:
            for line in f:
                deobfuscated = deobfuscate(line.strip(), max_depth=args.max_depth)
                logger.info(deobfuscated)


if __name__ == "__main__":
    main()
