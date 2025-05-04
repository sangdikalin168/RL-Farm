import mysql.connector
from mysql.connector import Error, pooling
from dotenv import load_dotenv
import os
import time

class MySQLService:
    """Handles MySQL database connections using Singleton and Connection Pooling."""
    
    _instance = None  # Singleton instance
    _connection_pool = None  # Connection Pool

    def __new__(cls, *args, **kwargs):
        """Ensure only one instance exists."""
        if cls._instance is None:
            cls._instance = super(MySQLService, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Load environment variables and create a connection pool."""
        env_path = os.path.join(os.path.dirname(__file__), "..", "..", ".env")  # Adjust the path if needed
        if os.path.exists(env_path):
            load_dotenv(env_path)
        else:
            print("⚠️ Warning: .env file not found!")

        self.db_config = {
            "host": os.getenv("DB_HOST", "203.176.133.252"),
            "user": os.getenv("DB_USER", "admin"),
            "password": os.getenv("DB_PASSWORD", "admin@MHG168"),
            "database": os.getenv("DB_NAME", "facebook_register"),
        }

        attempts = 3
        while attempts > 0:
            try:
                self._connection_pool = mysql.connector.pooling.MySQLConnectionPool(
                    pool_name="mypool",
                    pool_size=5,
                    **self.db_config
                )
                print("✅ MySQL Connection Pool Initialized")
                return
            except Error as e:
                print(f"❌ MySQL Connection Pool Error: {e}")
                attempts -= 1
                time.sleep(2)  # Retry delay
        
        print("❌ Failed to initialize MySQL Connection Pool after 3 attempts")
        self._connection_pool = None  # Prevents crashes

    def get_connection(self):
        """Get a connection from the pool."""
        if self._connection_pool is None:
            print("⚠️ MySQL Connection Pool is None! Attempting to reinitialize...")
            self._initialize()
        
        if self._connection_pool:
            try:
                return self._connection_pool.get_connection()
            except Error as e:
                print(f"❌ MySQL Connection Error: {e}")
                return None
        return None  # Prevents crashes

    def get_user_types(self):
        """Fetch unique user types from the database."""
        connection = self.get_connection()
        if not connection:
            return []

        query = "SELECT DISTINCT acc_type FROM created_users;"

        try:
            cursor = connection.cursor()
            cursor.execute(query)
            types = [row[0] for row in cursor.fetchall()]
            return types
        except Error as e:
            print(f"❌ Error fetching user types: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()  # ✅ Release connection back to the pool

    def get_users(self, user_type=None):
        """Fetch users from the created_users table, optionally filtered by type."""
        connection = self.get_connection()
        if not connection:
            return []

        query = """
        SELECT 
            id, uid, password, two_factor, email, pass_mail, acc_type, status, created_at 
        FROM created_users
        """

        params = ()
        if user_type and user_type != "All":
            query += " WHERE acc_type = %s"
            params = (user_type,)

        try:
            cursor = connection.cursor()
            cursor.execute(query, params)
            users = cursor.fetchall()
            return users
        except Error as e:
            print(f"❌ Error fetching users: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
                
    def save_user(self, uid, password, two_factor, email, pass_mail, acc_type):
        """Insert a new user into the created_users table."""
        connection = self.get_connection()
        if not connection:
            return False

        query = """
        INSERT INTO created_users 
        (uid, password, two_factor, email, pass_mail, acc_type, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, NOW())
        """
        params = (uid, password, two_factor, email, pass_mail, acc_type)

        try:
            cursor = connection.cursor()
            cursor.execute(query, params)
            connection.commit()
            return True
        except Error as e:
            print(f"❌ Error saving user: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()


    def save_gmail_account(self, first_name,last_name,gmail, password):
        """Insert a new user into the gmail_account table."""
        connection = self.get_connection()
        if not connection:
            return False

        query = """
        INSERT INTO gmail_account 
        (first_name,last_name,gmail, password)
        VALUES (%s, %s, %s, %s)
        """
        params = (first_name,last_name,gmail, password)

        try:
            cursor = connection.cursor()
            cursor.execute(query, params)
            connection.commit()
            return True
        except Error as e:
            print(f"❌ Error saving user: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()