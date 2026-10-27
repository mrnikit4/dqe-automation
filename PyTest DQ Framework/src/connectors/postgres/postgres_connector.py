
import pandas as pd
import psycopg2


class PostgresConnectorContextManager:
    def __init__(self, db_user: str, db_password: str, db_host: str,
                 db_name: str, db_port: int = 5432):
        self.db_user = db_user
        self.db_password = db_password
        self.db_host = db_host
        self.db_name = db_name
        self.db_port = db_port
        self.connection = None

    def __enter__(self):
        self.connection = psycopg2.connect(
            host=self.db_host,
            port=self.db_port,
            dbname=self.db_name,
            user=self.db_user,
            password=self.db_password,
        )
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        if self.connection is not None and not self.connection.closed:
            self.connection.close()

    def get_data_sql(self, sql: str) -> pd.DataFrame:
        if self.connection is None or self.connection.closed:
            raise RuntimeError("PostgreSQL connection is not open")
        with self.connection.cursor() as cursor:
            cursor.execute(sql)
            rows = cursor.fetchall()
            column_names = [description[0] for description in cursor.description]
        return pd.DataFrame(rows, columns=column_names)


