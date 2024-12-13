from typing import Annotated

from annotated_types import Len

VECTOR_DIM = 1536
Vector = Annotated[list[float], Len(VECTOR_DIM, VECTOR_DIM)]
