import sqlite3
from functools import wraps

def ensure_context(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        if self.connection is None:
            raise RuntimeError("Database must be used within a 'with' statement.")
        return method(self, *args, **kwargs)
    return wrapper

class Database:
    def __init__(self, db_name):
        self.db_name = db_name + '.db'
        self.connection = None
        self.cursor = None

    def __enter__(self):
        self.connection = sqlite3.connect('src/hookah_master_helper/database/' + self.db_name)
        self.cursor = self.connection.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()

    @ensure_context
    def execute(self, query: str, params: tuple = ()):
        try:
            self.cursor.execute(query, params)
        except sqlite3.Error as e:
            raise e


class DatabaseExecutor(Database):

    def create_table(self, table_name: str, columns: dict):
        if not columns:
            raise ValueError("Columns dictionary cannot be empty.")

        cols = ", ".join([f"{col_name} {data_type}" for col_name, data_type in columns.items()])
        query = f'CREATE TABLE IF NOT EXISTS {table_name} ({cols})'
        self.execute(query)

    def fetchone(self, table_name: str, fields: list = None, where: tuple = None):
        # If fields is None, select all columns
        # Expecting fields as a list of column names, e.g. ["id", "name"]
        if fields is None:
            fields_str = "*"
        else:
            # Join the column names into a comma-separated string
            fields_str = ", ".join(fields)

        query = f"SELECT {fields_str} FROM {table_name}"
        vals = ()

        # If where is provided, it's expected in the form (condition_str, values_tuple)
        # For example: ("id = ?", (1,))
        if where:
            condition_str, condition_vals = where
            query += f" WHERE {condition_str}"
            vals = condition_vals

        # Execute the query with parameterization
        self.execute(query, vals)
        return self.cursor.fetchone()

    def fetchall(self, table_name: str, fields: str = None, where: str = None, group_by: str = None, distinct=False):
        if not fields:
            fields = '*'  # Fetch all fields

        select = 'SELECT DISTINCT' if distinct else 'SELECT'
        query = f'{select} {fields} FROM {table_name} '
        if where:
            query += f'WHERE {where} '

        if group_by:
            query += f'GROUP BY {group_by}'

        self.execute(query)
        return self.cursor.fetchall()

    def update(self, table_name: str, values: list, where: list = None):
        # Expecting values in the form: [("field1", value1), ("field2", value2), ...]
        # Build the SET clause using parameter placeholders
        set_parts = [f"{field} = ?" for field, _ in values]
        set_clause = ", ".join(set_parts)

        query = f"UPDATE {table_name} SET {set_clause}"

        # Prepare the values list for parameter substitution
        vals = [v for _, v in values]

        # Handle WHERE clause if provided
        if where:
            # Expecting where in the form: [("field_name", value), ...]
            where_parts = [f"{w_field} = ?" for w_field, _ in where]
            where_clause = " AND ".join(where_parts)
            query += f" WHERE {where_clause}"
            vals.extend([w_val for _, w_val in where])

        # Convert vals to a tuple if the execute method expects it
        vals = tuple(vals)

        try:
            # Execute the parameterized query with a tuple of values
            cursor = self.execute(query, vals)
            self.connection.commit()
            # Returning the number of affected rows
            return cursor.rowcount
        except sqlite3.IntegrityError as e:
            # Raising a descriptive exception
            raise ValueError(f"Failed to update {table_name}: {e}")

    def insert(self, table_name: str, values: tuple, fields: tuple = None):
        if fields:
            fields_str = ', '.join(fields)
            placeholders = ', '.join(['?'] * len(values))
            query = f'INSERT INTO {table_name} ({fields_str}) VALUES ({placeholders})'
        else:
            placeholders = ', '.join(['?'] * len(values))
            query = f'INSERT INTO {table_name} VALUES ({placeholders})'

        try:
            self.execute(query, values)
        except sqlite3.IntegrityError as e:
            return f'{values} already exists: {e}\n'

        self.connection.commit()
        return None
