"""
Search module for GRKKMAI
"""

import re
import json
import random
from datetime import datetime
from typing import List, Dict, Optional, Any
from duckduckgo_search import DDGS


class GRKKMAI_Search:
    def __init__(self):
        self.ddgs = DDGS()
        self.conversation_context = []
        self.fact_database = {}
        self._pending_save = None  # ← ADDED: For consent flow

        self.knowledge_categories = {
            "general": ["what", "how", "why", "when", "where"],
            "technical": ["code", "programming", "software", "algorithm", "api"],
            "educational": ["learn", "study", "explain", "tutorial", "guide"],
            "current_events": ["news", "recent", "latest", "current", "today"],
            "definition": ["define", "meaning", "what is", "what are"],
            "comparison": ["vs", "versus", "compare", "difference", "better"]
        }

        print("✅ Advanced search system has been activated!")
    
    # ← ADDED: Method that ai_brain.py needs
    def _should_use_advanced_search(self, message: str) -> bool:
        """Check if user message requires web search"""
        triggers = [
            "what is", "who is", "explain", "how does", "why does",
            "tell me about", "information about", "learn about",
            "latest", "current", "recent", "news", "research"
        ]
        message_lower = message.lower()
        return any(trigger in message_lower for trigger in triggers)
    
    # ← ADDED: Method for using saved research
    def _generate_response_from_saved_research(self, query: str, saved_research: dict) -> str:
        """Generate response using previously saved research"""
        topic = saved_research.get("topic", "unknown topic")
        summary = saved_research.get("summary", "")
        sources = saved_research.get("sources", [])
        access_count = saved_research.get("access_count", 0)
        
        response = f"💾 I found saved research about '{topic}' that I think answers your question!\n\n"
        response += f"**From my previous research:**\n{summary}\n\n"
        
        if sources:
            response += "**Sources (from previous search):**\n"
            for i, source in enumerate(sources[:3], 1):
                title = source.get("title", "Unknown")[:60]
                url = source.get("url", "")
                response += f"{i}. {title}\n   {url}\n"
        
        response += f"\n✨ *(This research has been accessed {access_count} times)*\n\n"
        response += "Would you like me to search for more recent information, or does this help?"
        
        return response
    
    def analyze_question(self, user_message: str) -> Dict[str, Any]:
        """Analyze user question to understand intent and complexity"""
        message_lower = user_message.lower()

        analysis = {
            "intent": "general",
            "complexity": "simple",
            "needs_search": False,
            "search_queries": [],
            "response_type": "conversational",
            "key_concepts": []
        }

        # Determine intent
        for category, keywords in self.knowledge_categories.items():
            if any(keyword in message_lower for keyword in keywords):
                analysis["intent"] = category
                break
        
        # Is search needed?
        search_indicators = [
            "what is", "who is", "when did", "how does", "why does", 
            "latest", "current", "recent", "news about", "information about", 
            "explain", "tell me about", "research", "find out", "look up"
        ]

        if any(indicator in message_lower for indicator in search_indicators):
            analysis["needs_search"] = True
            analysis["search_queries"] = self._generate_search_queries(user_message)

        # How complex?
        complex_indicators = ["explain", "analyze", "compare", "detailed", "comprehensive", "advanced"]
        if any(indicator in message_lower for indicator in complex_indicators):
            analysis["complexity"] = "detailed"
        
        # Key concepts
        analysis["key_concepts"] = self._extract_key_concepts(user_message)

        return analysis
    
    def _generate_search_queries(self, user_message: str) -> List[str]:
        """Generate multiple search queries from user message"""
        message_clean = user_message.lower()

        # Remove question words to get the core query
        for word in ["what is", "who is", "tell me about", "explain", "how does", "why does"]:
            message_clean = message_clean.replace(word, "").strip()
        
        base_query = message_clean.strip()
        queries = [base_query]

        # Add variations for better coverage
        if len(base_query) > 3:
            queries.append(f"{base_query} explanation")
            queries.append(f"{base_query} guide")

        return queries[:3]  # Limit to 3 queries
    
    def _extract_key_concepts(self, text: str) -> List[str]:
        """Extract key concepts from text"""
        # Simple keyword extraction
        words = re.findall(r'\b\w+\b', text.lower())

        # Filter out common words
        stop_words = {
            "the", "is", "at", "which", "on", "and", "a", "an", "as", "are", "was",
            "were", "been", "be", "have", "has", "had", "do", "does", "did", "will",
            "would", "could", "should", "what", "how", "why", "when", "where", "who"
        }

        concepts = [word for word in words if len(word) > 3 and word not in stop_words]
        return concepts[:5]  # Top 5 concepts
    
    def search_and_analyze(self, queries: List[str], max_results_per_query: int = 3) -> Dict[str, Any]:
        """Search web and analyze results"""
        all_results = []

        for query in queries:
            try:
                results = self.ddgs.text(query, max_results=max_results_per_query)
                for result in results:
                    all_results.append({
                        "title": result.get("title", ""),
                        "url": result.get("href", ""),
                        "snippet": result.get("body", ""),
                        "query": query
                    })
            except Exception as e:
                print(f"Search error for '{query}': {e}")
                continue

        # Analyze and consolidate information
        analysis = {
            "total_sources": len(all_results),
            "key_information": self._extract_key_information(all_results),
            "sources": all_results,
            "consolidated_facts": self._consolidate_facts(all_results)
        }

        return analysis
    
    def _extract_key_information(self, results: List[Dict]) -> List[str]:
        """Extract key information from search results"""
        key_info = []

        for result in results:
            snippet = result.get("snippet", "")
            if snippet:
                # Extract "informative" sentences
                sentences = snippet.split('. ')
                for sentence in sentences:
                    if len(sentence) > 30 and any(word in sentence.lower() for word in 
                                                 ["is", "are", "can", "will", "provides", "offers", "includes"]):
                        key_info.append(sentence.strip())

        return key_info[:10]  # Top 10
    
    def _consolidate_facts(self, results: List[Dict]) -> Dict[str, List[str]]:
        """Consolidate facts from multiple sources"""
        facts = {
            "definitions": [],
            "features": [],
            "benefits": [],
            "examples": [],
            "statistics": []
        }

        for result in results:
            snippet = result.get("snippet", "").lower()

            # Definition lookup
            if any(word in snippet for word in ["is a", "refers to", "defined as", "means"]):
                facts["definitions"].append(result.get("snippet", ""))

            # Characteristics lookup
            if any(word in snippet for word in ["includes", "features", "consists of", "contains"]):
                facts["features"].append(result.get("snippet", ""))

            # Benefits lookup
            if any(word in snippet for word in ["benefits", "advantages", "helps", "improves"]):
                facts["benefits"].append(result.get("snippet", ""))

            # Example lookup
            if any(word in snippet for word in ["example", "such as", "including", "like"]):
                facts["examples"].append(result.get("snippet", ""))

            # Statistics/numbers lookup
            if re.search(r'\d+%|\d+,\d+|\$\d+', snippet):
                facts["statistics"].append(result.get("snippet", ""))

        # Category limit
        for key in facts:
            facts[key] = facts[key][:3]
        
        return facts
    
    def generate_intelligent_response(self, user_message: str, search_analysis: Optional[Dict] = None) -> str:
        """Generate intelligent, well-formatted response"""
        if not search_analysis:
            return self._generate_conversational_response(user_message)
        
        response_parts = []
        
        response_parts.append(self._generate_intro(user_message, search_analysis))
        response_parts.append(self._generate_main_content(search_analysis))

        if search_analysis.get("key_information"):
            response_parts.append(self._generate_key_points(search_analysis["key_information"]))

        response_parts.append(self._generate_sources_section(search_analysis.get("sources", [])))
        response_parts.append(self._generate_conclusion(user_message))

        return "\n\n".join(response_parts)

    def _generate_intro(self, user_message: str, search_analysis: Dict) -> str:
        """Generate introduction"""
        source_count = search_analysis.get("total_sources", 0)

        intros = [
            f"🔍 I searched the web and found information from {source_count} sources to help answer your question!",
            f"📚 Based on my search of {source_count} reliable sources, here's what I found:",
            f"✨ Let me share what I discovered from {source_count} sources about this topic:",
        ]

        return random.choice(intros)
    
    def _generate_main_content(self, search_analysis: Dict) -> str:
        """Generate main content from consolidated facts"""
        facts = search_analysis.get("consolidated_facts", {})
        content_parts = []

        if facts.get("definitions"):
            content_parts.append("**Definition:**")
            for definition in facts["definitions"][:1]:
                content_parts.append(f"• {definition[:200]}...")

        if facts.get("features"):
            content_parts.append("\n**Key Features:**")
            for feature in facts["features"][:2]:
                content_parts.append(f"• {feature[:150]}...")

        if facts.get("examples"):
            content_parts.append("\n**Examples:**")
            for example in facts["examples"][:2]:
                content_parts.append(f"• {example[:150]}...")

        return "\n".join(content_parts) if content_parts else "Here's what I found from the search results:"

    def _generate_key_points(self, key_information: List[str]) -> str:
        """Generate key points summary"""
        if not key_information:
            return ""
        
        points = ["**Key Points:**"]
        for i, info in enumerate(key_information[:5], 1):
            points.append(f"{i}. {info[:120]}...")

        return "\n".join(points)
    
    def _generate_sources_section(self, sources: List[Dict]) -> str:
        """Generate sources section"""
        if not sources:
            return ""
        
        sources_text = ["**Sources:**"]
        unique_sources = {}

        # Remove duplicates by URL
        for source in sources:
            url = source.get("url", "")
            if url not in unique_sources:
                unique_sources[url] = source

        for i, (url, source) in enumerate(list(unique_sources.items())[:5], 1):
            title = source.get("title", "Unknown")[:60]
            sources_text.append(f"{i}. {title}\n   {url}")

        return "\n".join(sources_text)
    
    def _generate_conclusion(self, user_message: str) -> str:
        """Generate conclusion"""
        conclusions = [
            "Would you like me to search for more specific information about any of these points?",
            "Is there a particular aspect you'd like me to explore further?",
            "Let me know if you need clarification on any of these points!",
            "I can dive deeper into any specific area that interests you the most."
        ]

        return random.choice(conclusions)
    
    def _generate_conversational_response(self, user_message: str) -> str:
        """Generate conversational response for non-search queries"""
        message_lower = user_message.lower()

        if any(greeting in message_lower for greeting in ["hello", "hi", "hey"]):
            return "Hello! I'm here to help you find information and answer questions. What would you like me to search about?"
        
        if "how are you" in message_lower:
            return "I'm doing great! Ready to help you research and learn about anything you're curious about. What's on your mind?"
        
        return "I'm not sure I have enough information to answer that well. Could you be more specific, or would you like me to search about it?"
    
    def process_query(self, user_message: str) -> str:
        """Main method to process any user query"""
        # Analyze the question
        analysis = self.analyze_question(user_message)

        # Add to conversation context
        self.conversation_context.append({
            "user_message": user_message,
            "analysis": analysis,
            "timestamp": datetime.now().isoformat()
        })

        # If search is needed, do comprehensive research
        if analysis["needs_search"] and analysis["search_queries"]:
            search_results = self.search_and_analyze(analysis["search_queries"])
            response = self.generate_intelligent_response(user_message, search_results)

            # Store pending save for consent flow
            self._pending_save = {
                "query": user_message,
                "results": search_results,
                "topic": analysis["key_concepts"][0] if analysis["key_concepts"] else user_message[:30]
            }

            # Store useful facts for future reference
            self._store_learned_facts(analysis["key_concepts"], search_results)
        else:
            response = self.generate_intelligent_response(user_message)

        return response
    
    def _store_learned_facts(self, concepts: List[str], search_results: Dict):
        """Store learned facts for future use"""
        for concept in concepts:
            if concept not in self.fact_database:
                self.fact_database[concept] = {
                    "facts": [],
                    "sources": [],
                    "last_updated": datetime.now().isoformat()
                }

            key_info = search_results.get("key_information", [])
            for info in key_info[:3]:
                if info not in self.fact_database[concept]["facts"]:
                    self.fact_database[concept]["facts"].append(info)

            sources = search_results.get("sources", [])
            for source in sources[:2]:
                source_info = f"{source.get('title', '')} - {source.get('url', '')}"
                if source_info not in self.fact_database[concept]["sources"]:
                    self.fact_database[concept]["sources"].append(source_info)

# Test the advanced AI system
if __name__ == "__main__":
    print("🧪 Testing Gurukukomi Advanced AI...")

    # Create advanced AI
    ai = GRKKMAI_Search()

    # Test questions
    test_questions = [
        "What is Python programming?",
        "Explain machine learning",
        "Hello, how are you?",
        "Latest news about AI development"
    ]

    for question in test_questions:
        print(f"\n{'='*50}")
        print(f"Question: {question}")
        print("="*50)

        response = ai.process_query(question)
        print(response)
        print("\n" + "-"*50)

    print("\n✅ Advanced AI system test complete!")
