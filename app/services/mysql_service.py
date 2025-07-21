import pymysql
from pymysql.err import MySQLError
from tkinter import messagebox
import time
import threading

class MySQLService:
    """Handles MySQL database connections using Singleton (no pooling in PyMySQL)."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        """Ensure only one instance exists."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(MySQLService, cls).__new__(cls)
                cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initialize the MySQL connection config."""
        self.db_config = {
            "host": "localhost",
            "user": "admin",
            "password": "admin@MHG168",
            "database": "test",
            "charset": "utf8mb4",
            "cursorclass": pymysql.cursors.Cursor,
            "autocommit": False
        }

    def get_connection(self):
        """Get a new database connection."""
        try:
            return pymysql.connect(**self.db_config)
        except MySQLError as e:
            messagebox.showerror("Database Error", f"❌ MySQL Connection Error: {e}")
            return None

    def get_user_types(self):
        query = "SELECT DISTINCT acc_type FROM created_users;"
        connection = self.get_connection()
        if not connection:
            return []

        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                return [row[0] for row in cursor.fetchall()]
        except MySQLError as e:
            messagebox.showerror("Database Error", f"❌ Error fetching user types: {e}")
            return []
        finally:
            connection.close()

    def get_users(self, user_type=None):
        connection = self.get_connection()
        if not connection:
            return []

        query = """
        SELECT id, uid, password, two_factor, email, pass_mail, acc_type, status, created_at 
        FROM created_users
        """
        params = ()
        if user_type and user_type != "All":
            query += " WHERE acc_type = %s"
            params = (user_type,)

        try:
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()
        except MySQLError as e:
            messagebox.showerror("Database Error", f"❌ Error fetching users: {e}")
            return []
        finally:
            connection.close()

    def update_user(self, uid, two_factor, email, acc_type):
        connection = self.get_connection()
        if not connection:
            return False

        query = """
        UPDATE created_users 
        SET two_factor = %s, email = %s, acc_type = %s
        WHERE uid = %s
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute(query, (two_factor, email, acc_type, uid))
            connection.commit()
            return True
        except MySQLError as e:
            messagebox.showerror("Database Error", f"❌ Error updating user: {e}")
            return False
        finally:
            connection.close()

    def save_user(self, uid, password, two_factor, email, pass_mail, acc_type):
        connection = self.get_connection()
        if not connection:
            return False

        query = """
        INSERT INTO created_users 
        (uid, password, two_factor, email, pass_mail, acc_type, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, NOW())
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute(query, (uid, password, two_factor, email, pass_mail, acc_type))
            connection.commit()
            return True
        except MySQLError as e:
            messagebox.showerror("Database Error", f"❌ Error saving user: {e}")
            return False
        finally:
            connection.close()

    def delete_user_by_type(self, user_type):
        connection = self.get_connection()
        if not connection:
            return False

        query = "DELETE FROM created_users WHERE acc_type = %s"
        try:
            with connection.cursor() as cursor:
                cursor.execute(query, (user_type,))
            connection.commit()
            return True
        except MySQLError as e:
            messagebox.showerror("Database Error", f"❌ Error deleting user: {e}")
            return False
        finally:
            connection.close()

    def save_gmail_account(self, first_name, last_name, gmail, password):
        connection = self.get_connection()
        if not connection:
            return False

        query = """
        INSERT INTO gmail_account 
        (first_name, last_name, gmail, password)
        VALUES (%s, %s, %s, %s)
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute(query, (first_name, last_name, gmail, password))
            connection.commit()
            return True
        except MySQLError as e:
            messagebox.showerror("Database Error", f"❌ Error saving Gmail account: {e}")
            return False
        finally:
            connection.close()
