"""
Database Module
Handles chat history storage using SQLite
"""

import sqlite3
from datetime import datetime
from typing import List, Dict
import json


class Database:
    def __init__(self, db_path: str = "chat_history.db"):
        """
        Initialize database connection
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.connect()
        self.create_tables()
    
    def connect(self):
        """Establish database connection"""
        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.cursor = self.conn.cursor()
            print(f"Connected to database: {self.db_path}")
        except Exception as e:
            raise Exception(f"Error connecting to database: {str(e)}")
    
    def create_tables(self):
        """Create necessary tables if they don't exist"""
        try:
            # Chat history table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS chat_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    user_message TEXT NOT NULL,
                    bot_response TEXT NOT NULL,
                    sources TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Documents table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    num_chunks INTEGER,
                    upload_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            self.conn.commit()
            print("Database tables created successfully")
        
        except Exception as e:
            raise Exception(f"Error creating tables: {str(e)}")
    
    def add_chat_message(self, session_id: str, user_message: str, 
                        bot_response: str, sources: List[Dict] = None):
        """
        Add a chat message to history
        
        Args:
            session_id: Session identifier
            user_message: User's question
            bot_response: Bot's answer
            sources: List of source documents used
        """
        try:
            sources_json = json.dumps(sources) if sources else None
            
            self.cursor.execute('''
                INSERT INTO chat_history (session_id, user_message, bot_response, sources)
                VALUES (?, ?, ?, ?)
            ''', (session_id, user_message, bot_response, sources_json))
            
            self.conn.commit()
        
        except Exception as e:
            raise Exception(f"Error adding chat message: {str(e)}")
    
    def get_chat_history(self, session_id: str = None, limit: int = 50) -> List[Dict]:
        """
        Retrieve chat history
        
        Args:
            session_id: Optional session ID to filter by
            limit: Maximum number of messages to retrieve
            
        Returns:
            List of chat messages
        """
        try:
            if session_id:
                self.cursor.execute('''
                    SELECT id, session_id, user_message, bot_response, sources, timestamp
                    FROM chat_history
                    WHERE session_id = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (session_id, limit))
            else:
                self.cursor.execute('''
                    SELECT id, session_id, user_message, bot_response, sources, timestamp
                    FROM chat_history
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (limit,))
            
            rows = self.cursor.fetchall()
            
            history = []
            for row in rows:
                history.append({
                    'id': row[0],
                    'session_id': row[1],
                    'user_message': row[2],
                    'bot_response': row[3],
                    'sources': json.loads(row[4]) if row[4] else None,
                    'timestamp': row[5]
                })
            
            return history
        
        except Exception as e:
            raise Exception(f"Error retrieving chat history: {str(e)}")
    
    def add_document(self, filename: str, file_path: str, num_chunks: int):
        """
        Add document record
        
        Args:
            filename: Name of the document
            file_path: Path to the document
            num_chunks: Number of chunks created
        """
        try:
            self.cursor.execute('''
                INSERT INTO documents (filename, file_path, num_chunks)
                VALUES (?, ?, ?)
            ''', (filename, file_path, num_chunks))
            
            self.conn.commit()
        
        except Exception as e:
            raise Exception(f"Error adding document: {str(e)}")
    
    def get_documents(self) -> List[Dict]:
        """
        Get all uploaded documents
        
        Returns:
            List of documents
        """
        try:
            self.cursor.execute('''
                SELECT id, filename, file_path, num_chunks, upload_timestamp
                FROM documents
                ORDER BY upload_timestamp DESC
            ''')
            
            rows = self.cursor.fetchall()
            
            documents = []
            for row in rows:
                documents.append({
                    'id': row[0],
                    'filename': row[1],
                    'file_path': row[2],
                    'num_chunks': row[3],
                    'upload_timestamp': row[4]
                })
            
            return documents
        
        except Exception as e:
            raise Exception(f"Error retrieving documents: {str(e)}")
    
    def clear_history(self, session_id: str = None):
        """
        Clear chat history
        
        Args:
            session_id: Optional session ID to clear specific session
        """
        try:
            if session_id:
                self.cursor.execute('DELETE FROM chat_history WHERE session_id = ?', (session_id,))
            else:
                self.cursor.execute('DELETE FROM chat_history')
            
            self.conn.commit()
            print("Chat history cleared")
        
        except Exception as e:
            raise Exception(f"Error clearing history: {str(e)}")
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            print("Database connection closed")


if __name__ == "__main__":
    # Test the database
    db = Database()
    print("Database initialized successfully!")
