import sqlite3
import os
from utils import hash_password

class Database:
    def __init__(self, db_file="forum.db"):
        """Initialize database connection and create tables if they don't exist"""
        self.db_file = db_file
        self.conn = None
        self.create_tables()
        
        # Create admin user if not exists
        if not self.get_user("admin"):
            self.add_user("admin", "admin123", "admin")
    
    def connect(self):
        """Connect to the SQLite database"""
        self.conn = sqlite3.connect(self.db_file)
        self.conn.row_factory = sqlite3.Row
        return self.conn
    
    def create_tables(self):
        """Create the necessary database tables if they don't exist"""
        conn = self.connect()
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
        ''')
        
        # Create messages table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            content TEXT NOT NULL
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_user(self, username, password, role="user"):
        """Add a new user to the database"""
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            hashed_password = hash_password(password)
            cursor.execute(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                (username, hashed_password, role)
            )
            conn.commit()
            result = True
        except sqlite3.IntegrityError:
            # Username already exists
            result = False
        finally:
            conn.close()
        
        return result
    
    def get_user(self, username):
        """Get user information by username"""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        
        conn.close()
        return dict(user) if user else None
    
    def save_message(self, username, content, timestamp):
        """Save a new message to the database"""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO messages (username, timestamp, content) VALUES (?, ?, ?)",
            (username, timestamp, content)
        )
        
        conn.commit()
        conn.close()
        return True
    
    def get_messages(self, limit=100):
        """Get the most recent messages"""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM messages ORDER BY id DESC LIMIT ?",
            (limit,)
        )
        
        messages = [dict(row) for row in cursor.fetchall()]
        messages.reverse()  # Show oldest messages first
        
        conn.close()
        return messages