import duckdb
import pandas as pd
from string import Template
from typing import List, Dict, Any, Union


class DuckDBHandler:
    def __init__(self, db_path: str = "data/raw/database.db"):
        self.conn = duckdb.connect(db_path)

    def __del__(self):
        if self.conn:
            self.conn.close()

    def create_table_if_not_exists(
        self, table_name: str, columns: Dict[str, str], recreate: bool = False
    ):
        if recreate:
            self._drop_table(table_name)

        column_defs = ", ".join([f"{col} {dtype}" for col, dtype in columns.items()])
        query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            {column_defs}
        )
        """
        self.conn.execute(query)

    def _drop_table(self, table_name: str):
        # Drop the table if it exists
        self.conn.execute(f"DROP TABLE IF EXISTS {table_name}")

    def insert_data(
        self,
        table_name: str,
        data: Union[Dict[str, Any], List[Dict[str, Any]], pd.DataFrame],
    ):

        if isinstance(data, pd.DataFrame):
            columns = {}
            for col_name, col_type in data.dtypes.items():
                if col_type == "object":
                    columns[col_name] = "TEXT"
                elif col_type == "int64":
                    columns[col_name] = "INTEGER"
                elif col_type == "float64":
                    columns[col_name] = "REAL"
                else:
                    columns[col_name] = "TEXT"

            self.create_table_if_not_exists(table_name, columns)
            # print(f"Created table : {table_name}")

            self.conn.register("temp_df", data)
            self.conn.execute(
                f"INSERT INTO {table_name} SELECT * FROM temp_df except select * from {table_name}"
            )
            self.conn.unregister("temp_df")
            # print(f"Data Successfully inserted into Table: {table_name}")
        else:
            # Handle dict or list of dicts
            if not isinstance(data, list):
                data = [data]

            if not data:
                return

            columns = ", ".join(data[0].keys())

            placeholders = ", ".join([f"${i+1}" for i in range(len(data[0]))])

            self.create_table_if_not_exists(table_name, columns)

            query = f"""
            INSERT INTO {table_name} ({columns})
            VALUES ({placeholders})
            """

            self.conn.executemany(query, [tuple(row.values()) for row in data])

    def execute_query(self, query: str, params: Union[tuple, Dict[str, Any]] = None):
        if params:
            return self.conn.execute(query, params).fetchall()
        return self.conn.execute(query).fetchall()

    def execute_template_query(self, query_template: str, params: Dict[str, Any]):
        template = Template(query_template)
        query = template.substitute(params)
        return self.execute_query(query)
