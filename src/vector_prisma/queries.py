from uuid import uuid4

from .operations import get_pgvector_operation
from .vector_type import Vector

class QueryBuilder:
    @staticmethod
    def build_insert_query(table_name: str, data: dict) -> str:
        columns = []
        return_columns = []
        values = []

        for attr, value in data.items():
            if attr == 'vec':
                vec_str = ", ".join(map(str, value))
                values.append(f"'[{vec_str}]'")
                return_columns.append(f'"{attr}"::text')
            else:
                columns.append(f'"{attr}"')
                values.append(f"'{value}'")
                return_columns.append(f'"{attr}"')

        columns_str = ", ".join(columns)
        values_str = ", ".join(values)
        returning_str = ", ".join([f'"{col}"' for col in columns])

        query = f"""
        INSERT INTO "{table_name}" ({columns_str})
        VALUES ({values_str})
        RETURNING {returning_str}
        """
        return query

    @staticmethod
    def build_upsert_query(table_name: str, where: dict, data: dict) -> str:
        columns = []
        return_columns = []
        values = []
        update_clauses = []

        for attr, value in data.items():
            if attr == 'vec':
                vec_str = ", ".join(map(str, value))
                values.append(f"'[{vec_str}]'")
                update_clauses.append(f'"{attr}" = EXCLUDED."{attr}"')
                columns.append(f'"{attr}"')
                return_columns.append(f'"{attr}"::text')
            else:
                columns.append(f'"{attr}"')
                values.append(f"'{value}'")
                update_clauses.append(f'"{attr}" = EXCLUDED."{attr}"')
                return_columns.append(f'"{attr}"')

        columns_str = ", ".join(columns)
        values_str = ", ".join(values)
        conflict_target = ", ".join([f'"{key}"' for key in where.keys()])
        returning_str = ", ".join([f'{col}' for col in return_columns])
        query = f"""
        INSERT INTO
        "{table_name}" ({columns_str})
        VALUES ({values_str})
        ON CONFLICT ({conflict_target})
        DO UPDATE SET
        "vec" = '[{vec_str}]'
        RETURNING {returning_str};
        """
        return query

    @staticmethod
    def build_find_query(table_name: str, where: dict) -> str:
        where_clauses = []
        for attr, value in where.items():
            if isinstance(value, list):
                value_str = ", ".join(f"'{v}'" for v in value)
                where_clauses.append(f'"{attr}" IN ({value_str})')
            else:
                where_clauses.append(f'"{attr}" = \'{value}\'')

        where_str = " AND ".join(where_clauses)
        query = f"""
        SELECT * FROM "{table_name}"
        WHERE {where_str}
        """
        return query
    
    @staticmethod
    def build_delete_query(table_name: str, where: dict) -> str:
        where_clauses = []
        for attr, value in where.items():
            if isinstance(value, list):
                value_str = ", ".join(f"'{v}'" for v in value)
                where_clauses.append(f'"{attr}" IN ({value_str})')
            else:
                where_clauses.append(f'"{attr}" = \'{value}\'')

        where_str = " AND ".join(where_clauses)
        query = f"""
        DELETE FROM "{table_name}"
        WHERE {where_str}
        """
        return query

    
    @staticmethod
    def build_nn_query(table_name: str, columns: list[str], query_vec: Vector, top_k: int, metric: str) -> str:
        columns_str = ", ".join(columns)
        vector_op = get_pgvector_operation("vec", query_vec, metric)
        
        query = f"""
        SELECT {columns_str}, {vector_op} AS distance
        FROM "{table_name}"
        ORDER BY distance
        LIMIT {top_k};
        """
        
        return query
    
    