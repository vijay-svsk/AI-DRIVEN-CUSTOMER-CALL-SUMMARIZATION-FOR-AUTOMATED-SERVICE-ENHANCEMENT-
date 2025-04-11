import sqlite3
import os
from cryptography.fernet import Fernet

class Database:
    """Handles database operations."""

    # Encryption Key (Should be securely stored in production)
    KEY = os.getenv("ENCRYPTION_KEY") or Fernet.generate_key()
    cipher = Fernet(KEY)

    def __init__(self, db_name="call_data.db"):
        self.db_name = db_name
        self.initialize_db()

    def get_db_connection(self):
        """Creates and returns a database connection."""
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        return conn

    def initialize_db(self):
        """Initializes the database tables."""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                contact TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS calls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                file_path TEXT,
                transcript TEXT,
                encrypted INTEGER DEFAULT 0,
                FOREIGN KEY(customer_id) REFERENCES customers(id)
            )
        ''')
        conn.commit()
        conn.close()

    def add_customer(self, name, contact):
        """Adds a new customer to the database."""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO customers (name, contact) VALUES (?, ?)", (name, contact))
        conn.commit()
        conn.close()

    def get_customer_by_name(self, name):
        """Retrieves customer details by name."""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM customers WHERE name = ?", (name,))
        customer = cursor.fetchone()
        conn.close()
        return customer

    def store_call(self, customer_name, file_path, transcript, encrypt=False):
        """Stores call metadata and optionally encrypts the transcript."""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        customer = self.get_customer_by_name(customer_name)
        
        if not customer:
            raise ValueError("Customer not found")
        
        encrypted_transcript = self.cipher.encrypt(transcript.encode()).decode() if encrypt else transcript
        
        cursor.execute(
            "INSERT INTO calls (customer_id, file_path, transcript, encrypted) VALUES (?, ?, ?, ?)",
            (customer["id"], file_path, encrypted_transcript, int(encrypt))
        )
        conn.commit()
        conn.close()

    def get_calls_by_customer(self, customer_name, decrypt=False):
        """Retrieves all call records for a specific customer."""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        customer = self.get_customer_by_name(customer_name)
        
        if not customer:
            return []
        
        cursor.execute("SELECT * FROM calls WHERE customer_id = ?", (customer["id"],))
        calls = cursor.fetchall()
        conn.close()
        
        results = []
        for call in calls:
            transcript = self.cipher.decrypt(call["transcript"].encode()).decode() if call["encrypted"] and decrypt else call["transcript"]
            results.append({
                "file_path": call["file_path"],
                "transcript": transcript,
                "encrypted": call["encrypted"]
            })
        
        return results
