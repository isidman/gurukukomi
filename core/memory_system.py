"""
GRKKMAI MEMORY SYSTEM
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional

class GRKKMAI_MEMORY:
    def __init__(self, db_path: str = "data/GRKKMAI_MEMORY.db"):
        """Initialize Memory System"""
        self.db_path= db_path
        self.setup_database()
        print("Gurukukomi memory system initialization complete!")

    def setup_database(self):
        conn = sqlite3.connect(self.db_path)

        #General convos table
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT NOT NULL,
            response TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            session_id TEXT
            )
            """
        )

        #Memory table
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS explicit_memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            memory_key TEXT NOT NULL,
            memory_value TEXT NOT NULL,
            memory_type TEXT DEFAULT 'preference',
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            user_consent BOOLEAN DEFAULT 1
            )
            """
        )

        #Memory consent table
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS concent_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT NOT NULL,
            memory_description TEXT,
            user_response TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        conn.commit()
        conn.close()
    
    def store_conversation(self, user_message: str, ai_response: str, session_id: str = "default"):
        """Basic conversation storage"""
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            """
            INSERT INTO conversations (message, response, session_id)
            VALUES (?, ?, ?)
            """, (user_message, ai_response, session_id))
        conn.commit()
        conn.close()

    def ask_to_remember(self, memory_key: str, memory_value: str, memory_type: str = "preference") -> str:
        """Ask for consent to remember something specific"""
        consent_question = f"""
            I'd like to remember that you {memory_key}: "{memory_value}"
            This would help a lot, in giving you better responses in future conversations.

            Are you okay with that?
            - Say "yes" or "remember it" to allow it.
            - Say "no" or "don't remember" to decline.
    
            This is completely optional and you can let me know if you change your mind anytime!
        """

        self._log_consent_request(memory_key, memory_value, memory_type)

        return consent_question.strip()
    
    def process_consent_response(self, user_response: str, memory_key: str, memory_value: str, memory_type: str = "preference") -> str:
        """Processing user's consent response"""
        response_lower = user_response.lower().strip()

        #positive keywords
        if any(word in response_lower for word in ["yes","remember","sure","okay","ok","allow","save"]):
            self._store_explicit_memory(memory_key, memory_value, memory_type, consent=True)
            self._log_consent_response(memory_key, "granted", user_response)
            return "Okay, got it! I'll remember that for future conversations. Thank you for letting me know!"
        
        #otherwise...
        elif any(word in response_lower for word in ["no","don't","nope","decline","refuse","never"]):
            self._log_consent_response(memory_key, "declined", user_response)
            return " Cool, I won't be remembering that. Let me know if you change your mind in the future."
        
        #not sure?
        else:
            return "I'm not so sure if you want me to remember that or not. Could you tell me 'yes' or 'no' so as to follow through with your decision?"
        
    def _store_explicit_memory(self, memory_key: str, memory_value: str, memory_type: str, consent: bool = True):
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
                     INSERT INTO explicit_memories (memory_key, memory_value, memory_type, user_consent)
                     VALUES (?, ?, ?, ?)
                     """, (memory_key, memory_value, memory_type, consent))
        conn.commit()
        conn.close()