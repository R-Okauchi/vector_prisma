from typing import Annotated

from annotated_types import Len
from prisma.models import OutlineEmbedding as OutlineEmbeddingBase


VECTOR_DIM = 1536
Vector = Annotated[list[float], Len(VECTOR_DIM, VECTOR_DIM)]

class OutlineEmbedding(OutlineEmbeddingBase):
    """OutlineEmbeddingのモデル"""
    vec: Vector
