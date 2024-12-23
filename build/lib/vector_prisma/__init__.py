__version__ = "0.0.0"

from typing import TYPE_CHECKING

from prisma import errors as errors
from prisma._config import config as config
from prisma._metrics import (
    Metric as Metric,
)
from prisma._metrics import (
    MetricHistogram as MetricHistogram,
)
from prisma._metrics import (
    Metrics as Metrics,
)
from prisma._types import PrismaMethod as PrismaMethod
from prisma.utils import setup_logging
from prisma.validator import *

# the import ordering is important here because
# we rely on the fact that `prisma/client.py` is the
# first piece of generated code that is loaded. This is
# especially useful for `python -m prisma_cleanup`
try:
    from .client import *  # noqa: I001, TID251
    from . import (
        types as types,  # noqa: TID251
        models as models,  # noqa: TID251
    )
except ModuleNotFoundError:
    # code has not been generated yet
    # TODO: this could swallow unexpected errors

    # we only define this magic function when the client has not
    # been generated for performance reasons and we hide it from
    # type checkers so that they don't incidentally disable type
    # checking due to the dynamic nature of the `__getattr__`
    # magic dunder method.
    if not TYPE_CHECKING:

        def __getattr__(name: str):
            try:
                return globals()[name]
            except KeyError as err:
                # TODO: support checking for 'models' here too
                if name in {"Prisma", "Client"}:
                    # TODO: remove this frame from the stack trace
                    raise RuntimeError(
                        "The Client hasn't been generated yet, "
                        "you must run `vector-prisma generate` before you can use the client.\n"
                    ) from None

                # leaves handling of this potential error to Python as per PEP 562
                raise AttributeError() from err


setup_logging()
