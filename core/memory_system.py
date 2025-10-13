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
            CREATE TABLE IF NOT EXISTS consent_log (
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
    
    def _log_consent_request(self, memory_key: str, memory_value: str, memory_type: str):
        """Remembering the times (?) GRKKMAI asked for consent"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
                     INSERT INTO consent_log (action, memory_description)
                     VALUES (?, ?)
                     """, ("consent_requested", f"{memory_type}: {memory_key} = {memory_value}"))
        conn.commit()
        conn.close()

    def _log_consent_response(self, memory_key: str, response_type: str, user_response: str):
        """Log user's yes or no"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            INSERT INTO consent_log (action, memory_description, user_response)
            VALUES (?, ?, ?)
            """, (f"consent_{response_type}", memory_key, user_response))
        conn.commit()
        conn.close()

    def get_explicit_memories(self) -> List[Dict]:
        """Get all memories user explicitly consented to"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("""
            SELECT memory_key, memory_value, memory_type, timestamp
            FROM explicit_memories
            WHERE user_consent = 1
            ORDER BY timestamp DESC
            """)
        
        memories = []
        for row in cursor.fetchall():
            memories.append({
                "key": row[0],
                "value": row[1],
                "type": row[2],
                "timestamp": row[3]
                })
            
        conn.close()
        return memories
        
    def find_memory(self, search_term: str) -> Optional[Dict]:
        """Key or value memory search"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("""
            SELECT memory_key, memory_value, memory_type, timestamp
            FROM explicit_memories
            WHERE (memory_key LIKE ? OR memory_value LIKE ?) AND user_consent = 1
            ORDER BY timestamp DESC
            LIMIT 1
        """, (f"%{search_term}%", f"%{search_term}%"))

        row = cursor.fetchone()
        conn.close()

        if row is None:
            return None

        if row:
            return {
                "key": row[0],
                "value": row[1],
                "type": row[2],
                "timestamp": row[3]
            }
        
    
    def forget_memory(self, memory_key: str) ->  bool:
        """Forget the things the user wants"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("""
            DELETE FROM explicit_memories
            WHERE memory_key LIKE ?              
        """, (f"%{memory_key}%",))

        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()

        if deleted:
            self._log_consent_response(memory_key, "forgotten", "user_requested_deletion")
        return deleted
    
    def get_memory_stats(self) -> Dict:
        """Get statistics about stored memories"""
        conn = sqlite3.connect(self.db_path)

        cursor = conn.execute("SELECT COUNT(*) FROM explicit_memories WHERE user_consent = 1")
        memory_count = cursor.fetchone()[0]

        cursor = conn.execute("SELECT COUNT(*) FROM consent_log WHERE date(timestamp) = date('now')")
        conversation_count = cursor.fetchone()[0]

        cursor = conn.execute("SELECT COUNT(*) FROM consent_log WHERE action = 'consent_requested'")
        consent_requests = cursor.fetchone()[0]

        conn.close()

        return {
            "memories_stored": memory_count,
            "conversations_today": conversation_count,
            "consent_requests_made": consent_requests
        }

    def clear_session_data(self):
        """Erase non-permanent conversation data"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("DELETE FROM conversations")
        conn.commit()
        conn.close()
        print("🧹 Session conversation data cleared (explicit memories preserved)")
