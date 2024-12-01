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
        self.connection = sqlite3.connect('database/' + self.db_name)
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
        """
        Creates a new table in the database with the specified name and columns.

        This method takes the name of the table and a dictionary that defines the columns
        of the table along with their data types. It constructs an SQL `CREATE TABLE` query
        and executes it, ensuring that the table is created if it does not already exist.

        Args:
            table_name (str): The name of the table to be created.
                              The name should follow SQL identifier conventions.
            columns (dict): A dictionary containing column names as keys and their SQL data types as values.
                           Example: {"id": "INTEGER PRIMARY KEY", "name": "TEXT", "age": "INTEGER"}.

        Raises:
            ValueError: If the `columns` dictionary is empty.
            RuntimeError: If the method is called outside a context manager (`with` block).
                          This is due to the requirement for an active database connection.

        Example:
            db.create_table("users", {"id": "INTEGER PRIMARY KEY", "username": "TEXT", "email": "TEXT"})
            This will create a table named `users` with three columns: `id`, `username`, and `email`.
        """
        if not columns:
            raise ValueError("Columns dictionary cannot be empty.")

        cols = ", ".join([f"{col_name} {data_type}" for col_name, data_type in columns.items()])
        query = f'CREATE TABLE IF NOT EXISTS {table_name} ({cols})'
        self.execute(query)

    def fetchone(self, table_name: str, fields: str = None, where: str = None):
        """
        Fetch a single record from the specified table in the database.

        This method constructs and executes an SQL `SELECT` query to fetch a single row from a given table.
        You can specify the fields to retrieve and optional conditions using the `where` parameter.
        If no fields are specified, all columns are selected by default.

        Args:
            table_name (str): The name of the table from which to fetch the record.
                              The name should follow SQL identifier conventions.
            fields (str, optional): A string specifying the columns to fetch. Defaults to `None`,
                                    which means all columns (`*`) will be fetched.
                                    Example: "id, name, email".
            where (str, optional): A conditional clause to specify which row to fetch.
                                   Example: "id = 1" or "name = 'John Doe'". Defaults to `None`,
                                   meaning no conditions, thus fetching the first row in the table.

        Returns:
            tuple or None: A tuple containing the values of the fetched row, or `None` if no matching row is found.

        Raises:
            RuntimeError: If the method is called outside a context manager (`with` block).
                          This is due to the requirement for an active database connection.

        Example:
            db.fetchone("users", fields="id, username", where="id = 1")
            This will fetch the `id` and `username` of the user where `id` equals 1.

        Notes:
            - Be careful when using the `where` parameter with user input to avoid SQL injection.
              Always sanitize or parameterize your queries where possible.
        """
        if not fields:
            fields = '*'  # Fetch all fields

        query = f'SELECT {fields} FROM {table_name}'
        if where:
            query += f' WHERE {where}'

        self.execute(query)
        return self.cursor.fetchone()

    def fetchmany(self, table_name: str, fields: str = None, where: str = None, group_by: str = None):
        """
        Fetch multiple records from the specified table in the database.

        This method constructs and executes an SQL `SELECT` query to fetch multiple rows from a given table.
        It allows specifying the fields to be retrieved, optional filtering conditions (`where`), and
        optional grouping conditions (`group_by`). If no fields are specified, all columns are selected by default.

        Args:
            table_name (str): The name of the table from which to fetch records.
                              The name should follow SQL identifier conventions.
            fields (str, optional): A string specifying the columns to fetch. Defaults to `None`,
                                    which means all columns (`*`) will be fetched.
                                    Example: "id, name, email".
            where (str, optional): A conditional clause to specify which rows to fetch.
                                   Example: "age > 18" or "status = 'active'". Defaults to `None`,
                                   meaning no conditions are applied, thus fetching all rows.
            group_by (str, optional): A clause to specify how to group the results.
                                      Example: "department_id" or "date_created". Defaults to `None`,
                                      meaning no grouping is applied.

        Returns:
            list of tuples or None: A list containing tuples of the fetched rows, or `None` if no matching rows are found.
                                    Each tuple represents a single row from the result set.

        Raises:
            RuntimeError: If the method is called outside a context manager (`with` block).
                          This is due to the requirement for an active database connection.

        Example:
            db.fetchmany("orders", fields="customer_id, SUM(amount)", where="status = 'shipped'", group_by="customer_id")
            This will fetch the `customer_id` and the total `amount` for all orders where the status is 'shipped',
            grouped by `customer_id`.

        Notes:
            - Use the `where` parameter with caution to avoid SQL injection. Always sanitize user input.
            - This method fetches up to 10,000 records at a time. You may need to adjust this logic
              if working with larger datasets or if you want to implement pagination.
        """
        if not fields:
            fields = '*'  # Fetch all fields

        query = f'SELECT {fields} FROM {table_name}'
        if where:
            query += f' WHERE {where}'

        if group_by:
            query += f' GROUP BY {group_by}'

        self.execute(query)
        return self.cursor.fetchmany(size=10000)

    def update(self, table_name: str, values: str, where: str = None):
        """
        Update records in the specified table of the database.

        This method constructs and executes an SQL `UPDATE` query to modify records in a given table.
        It allows specifying which records to update using the `where` parameter.
        If no `where` condition is provided, **all records in the table will be updated**, which should be used with caution.

        Args:
            table_name (str): The name of the table where the update operation should be performed.
                              The name should follow SQL identifier conventions.
            values (str): A string containing the column-value pairs to update.
                          Example: "name = 'John Doe', age = 30".
            where (str, optional): A conditional clause to specify which rows to update.
                                   Example: "id = 1" or "status = 'active'". Defaults to `None`,
                                   meaning all rows in the table will be updated.

        Returns:
            None

        Raises:
            RuntimeError: If the method is called outside a context manager (`with` block).
                          This is due to the requirement for an active database connection.
            sqlite3.DatabaseError: If an error occurs during the execution of the update query.

        Example:
            db.update("employees", values="salary = salary * 1.1", where="department = 'Sales'")
            This will update the `salary` of all employees in the `Sales` department, increasing it by 10%.

        Notes:
            - Be extremely cautious when using the `where` parameter. If omitted, **all records in the table will be updated**.
            - Use parameterized queries whenever possible to prevent SQL injection, especially if user input is involved.
        """
        query = f'UPDATE {table_name} SET {values}'
        if where:
            query += f' WHERE {where}'

        self.execute(query)
        self.connection.commit()

    def insert(self, table_name: str, values: str, fields: str = None):
        """
        Insert a new record into the specified table in the database.

        This method constructs and executes an SQL `INSERT INTO` query to add a new record into a given table.
        You can specify the columns for which the values are provided by using the `fields` parameter.
        If no `fields` are specified, it is assumed that values are provided for all columns.

        Args:
            table_name (str): The name of the table where the new record should be inserted.
                              The name should follow SQL identifier conventions.
            values (str): A string containing the values to insert. The values should be properly formatted
                          and match the columns specified in the `fields` parameter, if provided.
                          Example: "'John Doe', 30, 'johndoe@example.com'".
            fields (str, optional): A string specifying the columns for which the values are provided.
                                    Defaults to `None`, which means values are expected for all columns in the table.
                                    Example: "name, age, email".

        Returns:
            None

        Raises:
            RuntimeError: If the method is called outside a context manager (`with` block).
                          This is due to the requirement for an active database connection.
            sqlite3.DatabaseError: If an error occurs during the execution of the insert query.

        Example:
            db.insert("users", values="'John Doe', 30, 'johndoe@example.com'", fields="name, age, email")
            This will insert a new record into the `users` table with the specified values for the columns `name`, `age`, and `email`.

        Notes:
            - Be cautious when constructing the `values` string to avoid SQL injection.
              It is recommended to use parameterized queries to safely insert data, especially when using user input.
        """
        query = f'INSERT INTO {table_name} '
        if fields:
            query += f'({fields}) '
        query += f'VALUES {values}'

        try:
            self.execute(query)
        except sqlite3.IntegrityError:
            return f'{values} already exists\n'

        self.connection.commit()
        return None