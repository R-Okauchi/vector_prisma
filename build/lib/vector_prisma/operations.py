from enum import Enum

from .vector_type import Vector


class SearchMetric(str, Enum):
    L1_DISTANCE = "L1_DISTANCE"
    L2_DISTANCE = "L2_DISTANCE"
    INNER_PRODUCT = "INNER_PRODUCT"
    COSINE_DISTANCE = "COSINE_DISTANCE"


def get_pgvector_operation(
    column_name: str, query_vec: Vector, metric: SearchMetric
) -> str:
    vec_str = ", ".join(map(str, query_vec))
    op = ""

    if metric == SearchMetric.L1_DISTANCE:
        op = "<+>"
    elif metric == SearchMetric.L2_DISTANCE:
        op = "<->"
    elif metric == SearchMetric.INNER_PRODUCT:
        op = "<#>"
    elif metric == SearchMetric.COSINE_DISTANCE:
        if not any(query_vec):
            raise ValueError("Cosine distance is not defined for zero vectors")
        op = "<=>"
    else:
        raise ValueError(f"Invalid distance type: {metric}")

    return f"{column_name} {op} '[{vec_str}]'"
