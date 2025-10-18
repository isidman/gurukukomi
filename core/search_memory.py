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
        cursor = conn.cursor()

        #Stored search results
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS search_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL,
                topic TEXT NOT NULL,
                search_data TEXT NOT NULL,
                summary TEXT,
                key_facts TEXT,
                sources TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_consent INTEGER DEFAULT 1,
                access_count INTEGER DEFAULT 0,
                last_accessed DATETIME
            )
        """)

        #Consent tracking 
        cursor.execute("""
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

    def ask_to_save_search(self, query: str, search_results: Dict, topic: Optional[str] = None) -> str:
        if not topic:
            topic = query[:50] + "..." if len(query) > 50 else query

        source_count = len(search_results.get("sources", []))


        consent_question = f"""
I found some great information about "{topic}" from {source_count} sources:

Would you like me to save this research for future reference?
This would help me to give you faster, more informed resposes about this topic later.sorted

• Say "yes" or "save it" to store this research
• Say "no" or "don't save" to keep it temporary only  
• This is completely your choice and you can delete saved research anytime!

What would you prefer?
        """

        #logging consent request
        self._log_consent_request(query, topic)

        return consent_question.strip()
    
    def process_save_consent(self, user_response: str, query:str, search_results: Dict, topic: Optional[str] = None) -> str:
        response_lower = user_response.lower().strip()


        if not topic:
            topic = query[:50] + "..." if len(query) > 50 else query

        #Positive consent keywords
        if any(word in response_lower for word in ["yes", "save", "store", "keep", "sure", "okay", "ok", "allow"]):
            self._save_search_results(query, search_results, topic, consent=True)
            self._log_consent_response(query, "granted", user_response)
            return f" Perfect. I've saved the research about '{topic}' for future reference. I can now give you faster, more detailed answers about this topic anytime you ask!"
        
        #Negative consent keywords
        if any(word in response_lower for word in ["no", "don't", "nope", "decline", "refuse", "temporary"]):
            self._log_consent_response(query, "declined", user_response)
            return "No issues here. I'll keep this information temporary for our current conversation only. You can always ask me to research it again anytime!"
        
        #Unclear consent response
        else:
            return "I'm not sure if you want me to save this research or not. Could you say 'yes' to save it, or 'no' to keep it temporary?"
        

    def find_saved_research(self, topic_query: str) -> Optional[Dict]:
        conn = sqlite3.connect(self.db_path)

        #topic or query search
        cursor = conn.execute("""
            SELECT id, query, topic, search_data, summary, key_facts, sources, timestamp, access_count
            FROM search_results
            WHERE (topic LIKE ? OR query LIKE ?) AND user_consent = 1
            ORDER BY timestamp DESC
            LIMIT 1
        """, (f"%{topic_query}%", f"%{topic_query}%"))

        row = cursor.fetchone()

        if row:
            #update access count
            conn.execute("UPDATE search_results SET access_count = access_count + 1, last_accessed = ? WHERE id = ?", (datetime.now().isoformat(),row[0]))
            conn.commit()

            result = {
                "id": row[0],
                "query": row[1],
                "topic": row[2],
                "search_data": json.loads(row[3]) if row[3] else {},
                "summary": row[4],
                "key_facts": json.loads(row[3]) if row[3] else [],
                "sources": json.loads(row[6]) if row[6] else [],
                "timestamp": row[7],
                "access_count": row[8]
            }

            conn.close()
            return result
        
        conn.close()
        return None
        

    def _save_search_results(self, query: str, search_results: Dict, topic: str, consent: bool = True):
        conn = sqlite3.connect(self.db_path)

        #data preparation
        search_data_json = json.dumps(search_results)
        key_facts_json = json.dumps(search_results.get("key_information", []))
        sources_json = json.dumps([
            {"title": s.get("title", ""), "url": s.get("url", ""), "snippet": s.get("snippet", "")}

            for s in search_results.get("sources", [])
        ])

        summary = self._generate_summary(search_results)

        conn.execute("""
            INSERT INTO search_results(query, topic, search_data, summary, key_facts, sources, user_consent)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (query, topic, search_data_json, summary, key_facts_json, sources_json, consent))

        conn.commit()
        conn.close()

    def _generate_summary(self, search_results: Dict) -> str:
        key_info = search_results.get("key_information", [])
        if key_info:
            summary_points = key_info [:2]
            return ". ".join(point[:100] + "..." if len(point) > 100 else point for point in summary_points)
        else:
            source_count = len(search_results.get("sources", []))
            return f"Research from {source_count} sources with comprehensive information."

    def get_saved_topics(self) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)

        cursor = conn.execute("""
            SELECT topic, COUNT(*) as search_count, MAX(timestamp) as latest_search, SUM(access_count) as total_access
            FROM search_results
            WHERE user_consent = 1
            GROUP BY topic
            ORDER BY latest_search DESC
        """)

        topics = []
        for row in cursor.fetchall():
            topics.append({
                "topic": row[0],
                "search_count": row[1],
                "latest_search": row[2],
                "total_access": row[3] or 0
            })

        conn.close()
        return topics
    
    def delete_saved_research(self, topic: str) -> bool:
        conn = sqlite3.connect(self.db_path)

        cursor = conn.execute("DELETE FROM search_results WHERE topic LIKE ?", (f"%{topic}%",))
        deleted = cursor.rowcount > 0

        conn.commit()
        conn.close()

        return deleted
    
    def _log_consent_request(self, query: str, topic: str):
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            INSERT INTO search_consent (action, query_topic)
            VALUES (?, ?)
        """, ("save_consent_requested", f"{topic}: {query}"))
        conn.commit()
        conn.close()

    def _log_consent_response(self, query: str, response_type: str, user_response: str):
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            INSERT INTO search_consent (action, query_topic, user_response)
            VALUES (?, ?, ?)
        """, (f"save_consent_{response_type}", query, user_response))
        conn.commit()
        conn.close()

    def get_memory_stats(self) -> Dict:
        conn = sqlite3.connect(self.db_path)
        
        cursor = conn.execute("SELECT COUNT(*) FROM search_results WHERE user_consent = 1")
        saved_searches = cursor.fetchone()[0]

        cursor = conn.execute("SELECT COUNT(DISTINCT topic) FROM search_results WHERE user_consent = 1")
        unique_topics = cursor.fetchone()[0]

        cursor = conn.execute("SELECT SUM(access_count) FROM search_results WHERE user_consent = 1")
        total_access = cursor.fetchone()[0] or 0

        conn.close()

        return {
            "saved_searches": saved_searches,
            "unique_topics": unique_topics,
            "total_access_count": total_access
        }


# Test the search memory system
if __name__ == "__main__":
    print("🧪 Testing Search Result Memory System...")

    # Create memory system
    memory = SRM("test_search_memory.db")

    # Test data
    test_search_results = {
        "sources": [
            {"title": "Python Tutorial", "url": "https://example.com", "snippet": "Learn Python programming"},
            {"title": "Python Guide", "url": "https://example2.com", "snippet": "Complete Python guide"}
        ],
        "key_information": [
            "Python is a high-level programming language",
            "Python is widely used for web development and data science"
        ]
    }