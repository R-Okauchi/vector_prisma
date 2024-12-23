from typing import Any

from psycopg2 import sql

from .operations import SearchMetric, get_pgvector_operation


class QueryBuilder:
    @staticmethod
    def build_insert_query(
        table_name: str,
        data: dict[str, Any],
        uuid_columns: set[str] = set(),
        vector_columns: set[str] = set(),
    ) -> tuple[sql.SQL, list[Any]]:
        columns = list(data.keys())
        values = list(data.values())

        placeholders = []
        for i, col in enumerate(columns):
            if col in uuid_columns:
                placeholders.append(sql.SQL(f"${i+1}::uuid"))
            else:
                placeholders.append(sql.SQL(f"${i+1}"))

        columns_str = sql.SQL(", ").join(map(sql.Identifier, columns))
        values_str = sql.SQL(", ").join(placeholders)

        return_columns_str = sql.SQL(", ").join(
            [
                sql.SQL("{}::text").format(sql.Identifier(col))
                if col in vector_columns
                else sql.Identifier(col)
                for col in columns
            ]
        )

        query = sql.SQL("""
            INSERT INTO {table} ({columns})
            VALUES ({values})
            RETURNING {return_columns}
        """).format(
            table=sql.Identifier(table_name),
            columns=columns_str,
            values=values_str,
            return_columns=return_columns_str,
        )

        return query, values

    @staticmethod
    def build_update_query(
        table_name: str, where: dict[str, Any], data: dict[str, Any]
    ) -> tuple[sql.SQL, list[Any]]:
        set_clauses = []
        values = []
        where_clauses = []

        for attr, value in data.items():
            set_clauses.append(
                sql.SQL("{} = {}").format(sql.Identifier(attr), sql.Placeholder())
            )
            values.append(value)

        for attr, value in where.items():
            where_clauses.append(
                sql.SQL("{} = {}").format(sql.Identifier(attr), sql.Placeholder())
            )
            values.append(value)

        set_str = sql.SQL(", ").join(set_clauses)
        where_str = sql.SQL(" AND ").join(where_clauses)

        query = sql.SQL("""
            UPDATE {table}
            SET {set}
            WHERE {where}
            RETURNING id
        """).format(table=sql.Identifier(table_name), set=set_str, where=where_str)

        return query, values

    @staticmethod
    def build_upsert_query(
        table_name: str,
        where: dict[str, Any],
        data: dict[str, Any],
        uuid_columns: set[str] = set(),
        vector_columns: set[str] = set(),
    ) -> tuple[sql.SQL, list[Any]]:
        columns = []
        values = []
        update_clauses = []

        for attr, value in data.items():
            columns.append(attr)
            update_clauses.append(
                sql.SQL("{} = EXCLUDED.{}").format(
                    sql.Identifier(attr), sql.Identifier(attr)
                )
            )
            values.append(value)

        columns_str = sql.SQL(", ").join(map(sql.Identifier, columns))
        conflict_target = sql.SQL(", ").join(map(sql.Identifier, where.keys()))
        placeholders = []
        for i, col in enumerate(columns):
            if col in uuid_columns:
                placeholders.append(sql.SQL(f"${i+1}::uuid"))
            else:
                placeholders.append(sql.SQL(f"${i+1}"))
        values_str = sql.SQL(", ").join(placeholders)

        return_columns_str = sql.SQL(", ").join(
            [
                sql.SQL("{}::text").format(sql.Identifier(col))
                if col in vector_columns
                else sql.Identifier(col)
                for col in columns
            ]
        )

        query = sql.SQL("""
            INSERT INTO {table} ({columns})
            VALUES ({values})
            ON CONFLICT ({conflict_target})
            DO UPDATE SET {update}
            RETURNING {return_columns}
        """).format(
            table=sql.Identifier(table_name),
            columns=columns_str,
            values=values_str,
            conflict_target=conflict_target,
            update=sql.SQL(", ").join(update_clauses),
            return_columns=return_columns_str,
        )

        return query, values

    @staticmethod
    def build_find_query(
        table_name: str,
        columns: list[str],
        where: dict[str, Any] = {},
        vector_columns: set[str] = set(),
    ) -> tuple[sql.SQL, list[Any]]:
        where_clauses = []
        values = []
        if where:
            for i, (attr, value) in enumerate(where.items()):
                if isinstance(value, list):
                    value_str = ", ".join(f"${j+1}" for j in range(i, i + len(value)))
                    where_clauses.append(
                        sql.SQL("{} IN ({})").format(
                            sql.Identifier(attr), sql.SQL(value_str)
                        )
                    )
                    values.extend(value)
                else:
                    where_clauses.append(
                        sql.SQL("{} = ${}").format(
                            sql.Identifier(attr), sql.SQL(str(i + 1))
                        )
                    )
                    values.append(value)

        columns_str = sql.SQL(", ").join(
            [
                sql.SQL("{}::text").format(sql.Identifier(col))
                if col in vector_columns
                else sql.Identifier(col)
                for col in columns
            ]
        )

        where_str = sql.SQL(" AND ").join(where_clauses)
        query = sql.SQL("SELECT {columns} FROM {table}").format(
            columns=columns_str, table=sql.Identifier(table_name)
        )
        if where_clauses:
            query += sql.SQL(" WHERE {where}").format(where=where_str)
        return query, values

    @staticmethod
    def build_delete_query(
        table_name: str, where: dict[str, Any]
    ) -> tuple[sql.SQL, list[Any]]:
        where_clauses = []
        values = []
        for i, (attr, value) in enumerate(where.items()):
            if isinstance(value, list):
                value_str = ", ".join("%s" for _ in value)
                where_clauses.append(
                    sql.SQL("{} IN ({})").format(
                        sql.Identifier(attr), sql.SQL(value_str)
                    )
                )
                values.extend(value)
            else:
                where_clauses.append(sql.SQL("{} = %s").format(sql.Identifier(attr)))
                values.append(value)

        where_str = sql.SQL(" AND ").join(where_clauses)
        query = sql.SQL("DELETE FROM {table} WHERE {where}").format(
            table=sql.Identifier(table_name), where=where_str
        )

        return query, values

    @staticmethod
    def build_nn_query(
        table_name: str,
        columns: list[str],
        query_vec: list[float],
        vector_column: str,
        top_k: int,
        metric: SearchMetric,
    ) -> tuple[sql.SQL, list[Any]]:
        vector_op = get_pgvector_operation(vector_column, query_vec, metric)

        columns_str = sql.SQL(", ").join(
            [
                sql.SQL("{}::text").format(sql.Identifier(col))
                if col == vector_column
                else sql.Identifier(col)
                for col in columns
            ]
        )

        query = sql.SQL("""
            SELECT {columns}, {vector_op} AS distance
            FROM {table}
            ORDER BY distance
            LIMIT $1;
        """).format(
            columns=columns_str,
            vector_op=sql.SQL(vector_op),
            table=sql.Identifier(table_name),
        )

        return query, [top_k]
