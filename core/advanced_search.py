"""
Search module for GRKKMAI
"""

import re
import json
from datetime import datetime
from typing import List, Dict, Optional, Any
from duckduckgo_search import DDGS

class GRKKMAI_Search:
    def __init__(self):
        self.ddgs = DDGS()
        self.conversation_context = []
        self.fact_database = {}

        self.knowledge_categories = {
            "general": ["what", "how", "why", "when", "where"],
            "technical": ["code", "programming", "software", "algorithm", "api"],
            "educational": ["learn", "study", "explain", "tutorial", "guide"],
            "current_events": ["news","recent", "latest", "current", "today"],
            "definition": ["define", "meaning", "what is", "what are"],
            "comparison": ["vs", "versus", "compare", "difference", "better"]
        }

        print(" Advanced search system has been activated!")
    
    def analyze_question(self, user_message: str) -> Dict[str, Any]:
        message_lower = user_message.lower()

        analysis = {
            "intent": "general",
            "complexity": "simple",
            "needs_search": False,
            "search_queries": [],
            "response_type": "conversational",
            "key_concepts": []
        }

        #intent
        for category, keywords in self.knowledge_categories.items():
            if any(keyword in message_lower for keyword in keywords):
                analysis["intent"] = category
                break
        
        #is search needed?
        search_indicators = [
            "what is", "who is", "when did", "how does", "why does", "latest", "current", "recent", "news about", "information about", "explain", "tell me about", "research", "find out", "look up"
        ]

        if any(indicator in message_lower for indicator in search_indicators):
            analysis["needs_search"] = True
            analysis["search_queries"] = self._generate_search_queries(user_message)

        #how complex?
        complex_indicators = ["explain", "analyze", "compare", "detailed", "comprehensive", "advanced"]
        if any(indicator in message_lower for indicator in complex_indicators):
            analysis["complexity"] = "detailed"

        
        #key concepts
        analysis["key_concepts"] = self._extract_key_concepts(user_message)

        return analysis
    
    def _generate_search_queries(self, user_message: str) -> List[str]:
        """Generate multiple search queries from user message"""
        message_clean = user_message.lower()

        #remove question words to get the core query
        for word in ["what is", "who is", "tell me about", "explain", "how does", "why does"]:
            message_clean = message_clean.replace(word, "").strip()
            
        
        base_query = message_clean.strip()

        queries = [base_query]

        #Add varietions for better coverage
        if len(base_query) > 3:
            queries.append(f"{base_query} explanation")
            queries.append(f"{base_query} guide")

        return queries [:6]
    
    def _extract_key_concepts(self, text: str) -> List[str]:
        #simple keyword extraction
        words = re.findall(r'\b\w+\b', text.lower())

        #Filter out common words
        stop_words = {
            "the", "is", "at", "which", "on", "and", "a", "an", "as", "are", "was",
            "werer", "been", "be", "have", "has", "had", "do", "does", "did", "will",
            "would", "could", "should", "what", "how", "why", "when", "where", "who"
        }

        concepts = [word for word in words if len(word) > 3 and word not in stop_words]
        return concepts[:6]
    
    def search_and_analyze(self, queries: List[str], max_results_per_query: int = 6) -> Dict[str, Any]:

        #the main def happening
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

        #analyse and consolidate information
        analysis = {
            "total_sources": len(all_results),
            "key_information": self._extract_key_information(all_results),
            "sources": all_results,
            "consolidated_facts": self._consolidate_facts(all_results)
        }

        return analysis
    
    def _extract_key_information(self, results: List[Dict]) -> List[str]:
        key_info = []

        for result in results:
            snippet = result.get("snippet", "")
            if snippet:
                #extract "informative" sentences
                sentences = snippet.split('. ')
                for sentence in sentences:
                    if len(sentence) > 30 and  any(word in sentence.lower() for word in ["is", "are", "can", "will", "provides", "offers", "includes"]):
                        key_info.append(sentence.strip())

        return key_info[:10]
    
    def _consolidate_facts(self, results: List[Dict]) -> Dict[str, List[str]]:

        facts = {
            "definitions": [],
            "features": [],
            "benefits": [],
            "examples": [],
            "statistics": []
        }

        for result in results:
            snippet = result.get("snippet", "").lower()

            #definition lookup
            if any(word in snippet for word in ["is a", "refers to", "defined as", "means"]):
                facts["definitions"].append(result.get("snippet", ""))

            # characteristics lookup
            if any(word in snippet for word in ["includes", "features", "consists of", "contains"]):
                facts["features"].append(result.get("snippet", ""))

            #benefits lookup
            if any(word in snippet for word in ["benefits", "advantages", "helps", "improves"]):
                facts["benefits"].append(result.get("snippet", ""))

            #example lookup
            if any(word in snippet for word in ["example", "such as", "including", "like"]):
                facts["examples"].append(result.get("snippet", ""))

            #statistics/numbers lookup
            if re.search(r'\d+%|\d+,\d+|\$\d+', snippet):
                facts["statistics"].append(result.get("snippet", ""))

        #category limit
        for key in facts:
                facts[key] = facts[key][:6]
            
        return facts
    
    def generate_intelligent_response(self, user_message: str, search_analysis: Optional[Dict] = None) -> str:
        
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
        source_count = search_analysis.get("total_sources", 0)

        intros = [
            f"I searched the web and found information from {source_count} sources to help answer your question!",
            f"Based on my search of {source_count} reliable sources, here's what I found:",
            f"Let me share what I discovered from {source_count} sources about this topic:",
        ]

        import random
        return random.choice(intros)
    
    def _generate_main_content(self, search_analysis: Dict) -> str:
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
    

    def _generate_key_points(self, _extract_key_information: List[str]) -> str:
        if not key_information:
            return ""
        
        points = ["**Key Points:**"]
        for i, info in enumerate(key_information[:5], 1):
            points.append(f"{i}. {info[:120]}...")

        return "\n".join(points)
    
    def _generate_source_section(self, sources: List[Dict]) -> str:
        if not sources:
            return ""
        
        sources_text = ["**Sources:**"]
        unique_sources = []

        #remove duplicates by URL
        for source in sources:
            url = source.get("url", "")
            if url not in unique_sources:
                unique_sources[url] = source

        for i, (url, source) in enumerate(list(unique_sources.items())[:5], 1):
            title = source.get("title", "Unknown")[:60]
            sources_text.append(f"{i}. [{title}]({url})")

        return "\n".join(sources_text)
    
    def _generate_conclusion(self, user_message: str) -> str:
        conclusions = [
            "Would you like me to search for more specific information about any of these points?",
            "Is there a particular aspect you'd like me to explore further?",
            "let me know if you need clarification on any of these points!",
            "I can dive deeper into any specific area that interests you the most."
        ]

        import random
        return random.choice(conclusions)
    
    def _generate_conversational_response(self, user_message: str) -> str:
        # responses for non-search queries
        message_lower = user_message.lower()

        if any(greeting in message_lower for greeting in ["hello", "hi", "hey"]):
            return "Hello! I'm here to help you find information and answer questions. What would you like to me to search about?"
        
        if "how are you" in message_lower:
            return "I'm doing great! Ready to help your research and learn about anything you're curious about. What's on your mind?"
        
        return "I'm not sure I have enough information to answer that well. Could you be more specific, or would you like me to search about it?"
    
    def process_query(self, user_message: str) -> str:
        # Analyze the question
        analysis = self.analyze_question(user_message)

        #add to conversation context
        self.conversation_context.append({
            "user_message": user_message,
            "analysis": analysis,
            "timestamp": datetime.now().isoformat()
        })

        #if search is needed, do as comprehensive reasearch as you can
        if analysis["needs_search"] and analysis["search_queries"]:
            search_results = self.search_and_analyze(analysis["search_queries"])
            response = self.generate_intelligent_response(user_message, search_results)

            #store useful facts for future reference
            self._store_learned_facts(analysis["key_concepts"], search_results)
        else:
            response = self.generate_intelligent_response(user_message)

        return response
    
    def _store_learned_facts(self, concepts: List[str], search_results: Dict):
        for concept in concepts:
            if concept not in self.fact_database:
                self.fact_database[concept] = {
                    "facts": [],
                    "sources": [],
                    "last_updated": datetime.now().isoformat()
                }

            key_info = search_results.get("key_information", [])
            for info in key_info [:3]:
                if info not in self.fact_database[concept]["facts"]:
                    self.fact_database[concept]["facts"].append(info)

            sources = search_results.get("sources", [])
            for source in sources [:2]:
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
