import contextlib
import logging
import os
import sys
from typing import Iterator, List, NoReturn, Optional

from prisma import _sync_http as http
from prisma.utils import DEBUG

from ..generator.generator import Generator

__all__ = ("main", "setup_logging")

log: logging.Logger = logging.getLogger(__name__)


# TODO: switch base cli to click as well to support autocomplete


def main(
    args: Optional[List[str]] = None,
    use_handler: bool = True,
    do_cleanup: bool = True,
) -> NoReturn:
    if args is None:
        args = sys.argv

    with setup_logging(use_handler), cleanup(do_cleanup):
        if args[1] == "generate":
            generator = Generator()
            generator.invoke()
        if args[1] == "reset":
            generator = Generator()
            generator.reset()
    raise SystemExit(0)


@contextlib.contextmanager
def setup_logging(use_handler: bool = True) -> Iterator[None]:
    handler = None
    logger = logging.getLogger()

    try:
        if DEBUG:
            logger.setLevel(logging.DEBUG)

            # the prisma CLI binary uses the DEBUG environment variable
            if os.environ.get("DEBUG") is None:
                os.environ["DEBUG"] = "vector_prisma:GeneratorProcess"
            else:
                log.debug("Not overriding the DEBUG environment variable.")
        else:
            logger.setLevel(logging.INFO)

        if use_handler:
            fmt = logging.Formatter(
                "[{levelname:<7}] {name}: {message}",
                style="{",
            )
            handler = logging.StreamHandler()
            handler.setFormatter(fmt)
            logger.addHandler(handler)

        yield
    finally:
        if use_handler and handler is not None:
            handler.close()
            logger.removeHandler(handler)


@contextlib.contextmanager
def cleanup(do_cleanup: bool = True) -> Iterator[None]:
    try:
        yield
    finally:
        if do_cleanup:
            http.client.close()


if __name__ == "__main__":
    main()
