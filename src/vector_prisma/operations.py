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


def vec_str2vec(vec_str: str) -> list[float]:
    """
    文字列の形式 例"[1.0, 2.0, 3.0]" をfloatリスト [1.0, 2.0, 3.0] に変換する関数
    """
    return list(map(float, vec_str[1:-1].split(",")))
