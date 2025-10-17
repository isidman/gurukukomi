"""
Memory system for the Web Search.
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional, Any

#SRM = Search Result Memory
class SRM:
    def __init__(self, db_path: str = "data/search_memory.db"):
        """Initialization of search result storage with consent system"""
        self.db_path = db_path
        self.setup_database()
        print(" Search result memory (SRM) System initialized.")

    def setup_database(self):
        """Create database tables for search results and concent"""
        conn = sqlite3.connect(self.db_path)

        #Stored search results
        conn.execute("""
            CREATE TABLE IF NOT EXISTS search_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL,
                topic TEXT NOT NULL,
                search_data TEXT NOT NULL,
                summary TEXT,
                key_facts TEXT,
                sources TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_concent BOOLEAN DEFAULT 1,
                access_count INTEGER DEFAULT 0,
                last_accessed DATETIME
            )
        """)

        #Consent tracking 
        conn.execute("""
            CREATE TABLE IF NOT EXISTS search_consent(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action TEXT NOT NULL,
                query_topic TEXT,
                user_response TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()