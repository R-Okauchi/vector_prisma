from typing import Any, get_args
from uuid import UUID

from annotated_types import Len


class VectorBase:
    VECTOR_DIM: int

    @classmethod
    def find_vector_columns_from_model(cls, d: dict[str, Any]) -> set[str]:
        vector_columns = set()
        for key, value in d.items():
            args = get_args(value)
            if (
                args
                and args[0] == list[float]
                and args[1] == Len(cls.VECTOR_DIM, cls.VECTOR_DIM)
            ):
                vector_columns.add(key)
        return vector_columns

    @classmethod
    def find_uuid_vector_columns(
        cls, data: dict[str, Any]
    ) -> tuple[set[str], set[str]]:
        uuid_columns = set()
        vector_columns = set()
        for key, value in data.items():
            if isinstance(value, UUID):
                uuid_columns.add(key)
            elif (
                isinstance(value, list)
                and len(value) == cls.VECTOR_DIM
                and all(isinstance(i, float) for i in value)
            ):
                vector_columns.add(key)
        return uuid_columns, vector_columns
