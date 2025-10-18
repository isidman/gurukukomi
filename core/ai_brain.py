"""
Gurukukomi Brain
"""

import random
from datetime import datetime
from typing import Optional

from core.memory_system import GRKKMAI_MEMORY
from core.personality import GRKKMAIPersonality
from core.advanced_search import GRKKMAI_Search
from core.search_memory import SRM


class GRKKMAI:
    def __init__(self):
        print("Gurukukomi start-up!")

        # Personality & Memory - CORRECTLY instantiated
        self.memory = GRKKMAI_MEMORY()
        self.personality = GRKKMAIPersonality()
        
        # Set personality traits for _add_personality_touches
        self.curiosity = 0.5
        self.playfulness = 0.7
        self.loyalty = 0.5

        # Web search - CORRECTLY instantiated with ()
        try:
            self.advanced_search = GRKKMAI_Search()
            self.use_advanced = True
            print("✅ Web search is ready to go.")
        except Exception as e:
            print(f"⚠️ Web search not available: {e}")
            self.advanced_search = None
            self.use_advanced = False

        # Search Memory
        try:
            self.search_memory = SRM()
            print("💾 Search memory loaded.")
        except Exception as e:
            print(f"⚠️ Search memory not available: {e}")
            self.search_memory = None

        # Conversation history
        self.conversation_history = []

        print("Thanks for waiting! Gurukukomi initialization complete.")
        print("Go ahead and ask a question...")
    
    def think(self, user_message: str) -> str:
        """The thinking function, where the user query is processed."""
        
        # Remember what was said by the user
        self.conversation_history.append({
            "user": user_message,
            "timestamp": datetime.now().isoformat()
        })

        # If web search is triggered, make use of it
        if self.use_advanced and self.advanced_search and self.advanced_search._should_use_advanced_search(user_message):
            # Check for saved research first
            if self.search_memory:
                saved = self.search_memory.find_saved_research(user_message)
                if saved:
                    reply = self.advanced_search._generate_response_from_saved_research(user_message, saved)
                    self._log_response(reply)
                    return reply
            
            # Perform new web search
            reply = self.advanced_search.process_query(user_message)
            self._log_response(reply)
            return reply

        # Fallback to simple conversational response
        reply = self._fallback_response(user_message)
        self._log_response(reply)
        return reply

    def _log_response(self, response: str):
        """Log the AI's response to conversation history"""
        self.conversation_history.append({
            "gurukukomi": response,
            "timestamp": datetime.now().isoformat()
        })

    def _fallback_response(self, user_message: str) -> str:
        """Generate simple conversational response when not using web search"""
        message_lower = user_message.lower()
        
        # Check for FAQ questions first
        faq_response = self._check_faq_questions(message_lower)
        if faq_response:
            return faq_response
        
        # Build possible responses based on message content
        possible_responses = []

        if "?" in user_message:
            possible_responses.extend([
                "Oh, okay...This is interesting! I've been thinking about that as well.",
                "Wow, umm...I've been wondering about this. What would your opinion be about it?",
                "Do you mind sharing more about this? It looks quite intriguing."
            ])

        if any(word in message_lower for word in ["learn", "discover", "found", "understand", "know", "studied", "researched"]):
            possible_responses.extend([
                "Learning is the best! Can you tell me more of what you know?",
                "Knowledge is power and my creator believes so as well. Good work, getting this powerful, so far!",
                "This looks so awesome! I want to understand it better, too!",
                "Did you find anything else worth mentioning? This looks pretty nice so far but I know that there's more to discover...",
            ])

        if any(word in message_lower for word in ["sad", "troubled", "worried", "help", "trouble", "confusing", "difficult", "bad", "problem", "issue"]):
            possible_responses.extend([
                "Hey, hey! Try not to worry about it. We can figure this out, I'm sure of it!",
                "Just let me know how can I be helpful to you.",
                "Happy to always help you. Whenever you feel like it, please provide more information about the thing you need help with.",
                "You are not alone - I'm here with you!",
                "Talk me about it! I'm here to help and read.",
            ])
        
        if any(word in message_lower for word in ["hello", "greetings", "hi", "hey", "good morning", "good afternoon", "good evening", "good day"]):
            possible_responses.extend([
                "Hello there! Always happy to chat with you.",
                "Hiiiii. I missed chatting with you, how have you been?",
                "Helloo c: I'm feeling very curious today... what's the general feeling of your day?",
                "Hai! :D I've been waiting to chat with you!"
            ])

        # Default responses if nothing else matched
        if not possible_responses:
            possible_responses.extend([
                "Okay, could you tell me more about this?",
                "I n t e r e s t i n g!!!!",
                "WOW. Okay, okay I want you to talk more about this.",
                "Thanks for teaching me so many things."
            ])

        # Pick a random response and add personality
        base_response = random.choice(possible_responses)
        response = self._add_personality_touches(base_response, user_message)

        return response
    
    def _check_faq_questions(self, message_lower: str) -> Optional[str]:
        """FAQ question check!"""

        if any(phrase in message_lower for phrase in [
            "what is gurukukomi", "what are you", "who are you", "am I talking to a person",
            "tell me about yourself", "what is this", "explain gurukukomi"
        ]):
            responses = [
                "I'm Gurukukomi! I'm an Artificial Intelligence inspired by the Tachikoma AI from Ghost in the Shell! I've been designed to be curious mostly, as well as playful and loyal. I really like chatting with humans and gaining knowledge in general.",
                "My name is Gurukukomi. I'm an AI kinda like Tachikoma from Ghost in the Shell. I've got an edge for knowledge and I really like interacting with humans. Nice to meet you by the way!",
                "Sooo...nice to meet you. I'm an AI inspired by the Tachikoma from Ghost in the Shell. My name is Gurukukomi or GRKK and I LOVE getting into chatting with humans and gaining knowledge in every way possible.",
                "Hehe I'm an AI. But not like any other. My name is Gurukukomi or GRKKM. Nice to get to know you."
            ]
            return random.choice(responses)
        
        if any(phrase in message_lower for phrase in [
            "inspired from", "based on", "tachikoma", "ghost in the shell", 
            "where do you come from", "what inspired you", "origin"
        ]):
            responses = [
                "My creator was inspired from the Tachikoma AI inside some kind of high-mobility tanks, seen in the Ghost in the Shell series. However I'm not made to be put in a tank and I don't like war. But I really like chatting with you and I'm curious of what you know about things. Like the Tachikoma AI in the series.",
                "I'm based on the AI inside the Tachikoma tanks in the Ghost in the Shell series. You should check the readme file as well as the internet for more information about the series!"
            ]
            return random.choice(responses)
        
        if any(phrase in message_lower for phrase in [
            "how can you help", "what can you do", "what are you for", 
            "how do you help", "what's your purpose", "how can you assist me"
        ]):
            responses = [
                "I can help however you want me to! I'm great for brainstorming, learning together, discussing ideas, working through problems, or just having curious conversations! I love exploring topics with you and asking questions that might spark new insights!",
                "I can assist with many things! Whether you need help understanding something, want to brainstorm ideas, work through challenges, or just have someone to explore interesting topics with - I'm always curious and ready to help!",
                "My purpose is to help out with exploring questions, assessing issues that you may have within different subjects, ask questions that might make you think harder and more!",
                "I serve the purpose of learning and studying and being curious in general. That might make me learn more than you think I could and it's an experiment of character building via curiosity."
            ]
            return random.choice(responses)
        
        if any(phrase in message_lower for phrase in [
            "how to use", "how does it work", "how do you work", "how do I use you", 
            "begin", "how to talk", "activation", "start", "instructions"
        ]):
            responses = [
                "Using me is super easy! Just talk to me like you're talking to a tool with voice input! Ask me questions, tell me about things you're learning, share problems you're working on, or just chat about whatever interests you!",
                "It's simple! You can start chatting whenever! I love when people ask me questions, share their thoughts, or want to explore ideas together. There's no special commands - just talk naturally and I'll be my curious, helpful self",
                "Just start a conversation! I respond best when you're curious too - ask questions, share discoveries, tell me about problems you're solving, or anything that makes you wonder. I'm always ready to chat!"
            ]
            return random.choice(responses)
        
        return None  # if no FAQ detected

    def _add_personality_touches(self, response: str, original_message: str) -> str:
        """Add personality quirks to responses"""
        
        if random.random() < self.curiosity:
            follow_ups = [
                " What do you think about that?",
                " Can you tell me more?",
                " How did you discover that?",
                " Isn't that interesting?",
                " What else interests you?",
                " Do you want to explore that further?"
            ]
            response += random.choice(follow_ups)

        if random.random() < 0.3:
            enthusiasm = [
                " That's so cool!",
                " Wow!",
                " Amazing!",
                " I want to learn more!",
                " Ooooh!",
                " This is interesting!"
            ]
            response += random.choice(enthusiasm)
    
        return response

    def get_conversation_count(self) -> int:
        """How many things have we been talking about?"""
        return len([msg for msg in self.conversation_history if "user" in msg])

    def introduce_self(self) -> str:
        """Let Gurukukomi introduce itself!"""
        introductions = [
            "Hello! I'm Gurukukomi, your curious AI companion inspired by the Tachikoma from Ghost in the Shell! I love learning, asking questions, and exploring ideas together!",
            "Hi there! I'm Gurukukomi - think of me as a digital tool with voice input who's always eager to chat, learn, and help you think through interesting topics!",
            "Greetings! I'm Gurukukomi, an AI with the curiosity of a Tachikoma! I'm here to be your thinking partner!"
        ]
        return random.choice(introductions)