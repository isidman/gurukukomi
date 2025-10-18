"""
GRKKMAI Chat Interface - Command-line Version
"""

import os
import sys
from datetime import datetime

# Adding parent dir so modules can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.ai_brain import GRKKMAI


class GRKKMCLI:
    def __init__(self):
        print("🤖 Starting up Gurukukomi Chat Interface...")
        print("="*50)

        try:
            # Full system initialization - GRKKMAI handles all subsystems internally
            self.ai = GRKKMAI()
            
            print("="*50)
            print("✅ Gurukukomi is ready for interaction!")
            print()

        except Exception as e:
            print(f"❌ Error initializing Gurukukomi: {e}")
            sys.exit(1)
    
    def start_chat(self):
        """Start the main chat loop"""
        self.print_welcome()

        while True:
            try:
                user_input = input("\n👤 You: ").strip()

                # Handle special commands
                if self.handle_special_commands(user_input):
                    continue

                # Skip empty messages
                if not user_input:
                    continue

                # Get AI response
                print("\n🤖 Gurukukomi: ", end="", flush=True)
                response = self.ai.think(user_input)
                print(response)

                # Handle consent for saving search results
                if (self.ai.search_memory and 
                    self.ai.advanced_search and 
                    getattr(self.ai.advanced_search, "_pending_save", None)):
                    
                    # Store pending_save in a variable to avoid type errors
                    pending = self.ai.advanced_search._pending_save
                    
                    # Only proceed if pending is actually a dict
                    if pending and isinstance(pending, dict):
                        choice = input("\n💾 Your choice: ").strip()
                        consent_response = self.ai.search_memory.process_save_consent(
                            choice,
                            pending["query"],
                            pending["results"],
                            pending["topic"]
                        )
                        print(consent_response)
                        # Clear pending save
                        self.ai.advanced_search._pending_save = None


            except KeyboardInterrupt:
                print("\n\n👋 Goodbye! Thanks for chatting with Gurukukomi!")
                break
            except EOFError:
                print("\n\n👋 Chat ended. Bye, bye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                print("Let's keep chatting though!")

    def handle_special_commands(self, user_input):
        """Handle special chat commands"""
        command = user_input.lower().strip()

        # Help
        if command in ["/help", "help", "commands"]:
            self.print_help()
            return True
        
        # Quit
        elif command in ["/quit", "/exit", "quit", "exit", "goodbye", "bye"]:
            print("\n👋 Goodbye! Thanks for chatting with Gurukukomi!")
            sys.exit(0)
        
        # Stats
        elif command in ["/stats", "stats", "statistics"]:
            self.print_stats()
            return True

        # Memory
        elif command in ["/memory", "memory", "what do you remember"]:
            self.print_memory_info()
            return True
        
        # Personality
        elif command in ["/personality", "personality", "how are you feeling"]:
            self.print_personality_info()
            return True

        # Saved research
        elif command in ["/saved", "saved research", "saved topics"]:
            self.print_saved_research()
            return True

        # Clear
        elif command in ["/clear", "clear"]:
            os.system('clear' if os.name == 'posix' else 'cls')
            self.print_welcome()
            return True

        return False
    
    def print_welcome(self):
        """Print welcome message"""
        print("\n🤖 GURUKUKOMI CHAT INTERFACE")
        print("="*40)
        print("💬 Just type your message and press Enter!")
        print("❓ Type '/help' for special commands")
        print("🚪 Type '/quit' to exit")
        print("-"*40)

    def print_help(self):
        """Print available commands"""
        print("\n📋 AVAILABLE COMMANDS:")
        print("-"*40)
        print("💬 Just type normally to chat")
        print("/help        - Show this help")
        print("/quit        - Exit the chat")
        print("/stats       - Show conversation stats")
        print("/memory      - Show what I remember")
        print("/personality - Show my current mood")
        print("/saved       - Show saved research topics")
        print("/clear       - Clear the screen")
        print("-"*40)

    def print_stats(self):
        """Print conversation statistics"""
        print("\n📊 CONVERSATION STATS:")
        print("-"*40)

        # Basic conversation count
        if hasattr(self.ai, 'conversation_history'):
            total_exchanges = len([msg for msg in self.ai.conversation_history if "user" in msg])
            print(f"💬 Total conversations: {total_exchanges}")

        # Memory stats
        if self.ai.memory:
            try:
                memory_stats = self.ai.memory.get_memory_stats()
                print(f"💾 Memories stored: {memory_stats.get('memories_stored', 0)}")
                print(f"🗣️ Conversations today: {memory_stats.get('conversations_today', 0)}")
            except Exception as e:
                print(f"💾 Memory stats unavailable: {e}")

        # Personality stats
        if self.ai.personality:
            try:
                personality_summary = self.ai.personality.get_personality_summary()
                dominant_traits = personality_summary.get('dominant_traits', [])
                if dominant_traits:
                    print(f"🎭 Top personality traits: {', '.join(dominant_traits[:3])}")
            except Exception as e:
                print(f"🎭 Personality stats unavailable: {e}")

        # Search memory stats
        if self.ai.search_memory:
            try:
                search_stats = self.ai.search_memory.get_memory_stats()
                print(f"🔍 Saved searches: {search_stats.get('saved_searches', 0)}")
                print(f"📚 Unique topics: {search_stats.get('unique_topics', 0)}")
            except Exception as e:
                print(f"🔍 Search stats unavailable: {e}")

        print("-"*40)

    def print_memory_info(self):
        """Print memory information"""
        print("\n💾 MEMORY INFO:")
        print("-"*40)

        if not self.ai.memory:
            print("❌ Memory system not available")
            return
        
        try:
            memories = self.ai.memory.get_explicit_memories()
            if not memories:
                print("📝 No memories stored yet!")
                print("💡 I only remember things you explicitly ask me to remember!")
            else:
                print(f"📚 I remember {len(memories)} things about you:")
                for memory in memories[-5:]:  # Show last 5 memories
                    print(f"  • {memory['key']}: {memory['value']}")
                if len(memories) > 5:
                    print(f"  ... and {len(memories) - 5} more things")
        except Exception as e:
            print(f"❌ Error accessing memories: {e}")

        print("-"*40)

    def print_personality_info(self):
        """Print personality information"""
        print("\n🎭 PERSONALITY INFO:")
        print("-"*40)

        if not self.ai.personality:
            print("❌ Personality engine not available")
            return
        
        try:
            summary = self.ai.personality.get_personality_summary()
            
            print(f"😊 Current mood: {summary.get('mood', 'Unknown')}")
            print("🎯 Top traits:")

            traits = summary.get('traits', {})
            for trait_name, trait_value in list(traits.items())[:3]:
                percentage = int(trait_value * 100)
                print(f"  • {trait_name.title()}: {percentage}%")
            
            evolution_events = summary.get('evolution_events', 0)
            print(f"🌱 Personality has evolved {evolution_events} times")
        
        except Exception as e:
            print(f"❌ Error accessing personality: {e}")

        print("-"*40)

    def print_saved_research(self):
        """Print saved research topics"""
        print("\n💾 SAVED RESEARCH:")
        print("-"*40)

        if not self.ai.search_memory:
            print("❌ Search memory not available")
            return
        
        try:
            topics = self.ai.search_memory.get_saved_topics()
            stats = self.ai.search_memory.get_memory_stats()
            
            print(f"📊 Total saved: {stats['saved_searches']} searches on {stats['unique_topics']} topics")
            print(f"🔍 Total accessed: {stats['total_access_count']} times")
            print()
            
            if topics:
                print("📚 Saved topics:")
                for topic_info in topics[:10]:  # Show top 10
                    name = topic_info['topic'][:40]
                    count = topic_info['total_access']
                    print(f"  • {name} (accessed {count} times)")
            else:
                print("📝 No saved research yet.")
                print("💡 Ask me questions and choose to save the results!")
            
        except Exception as e:
            print(f"❌ Error accessing saved research: {e}")

        print("-"*40)


def main():
    """Main function to start the chat interface"""
    try:
        cli = GRKKMCLI()
        cli.start_chat()
    except Exception as e:
        print(f"❌ Failed to start Gurukukomi: {e}")
        print("Make sure all core modules are properly set up!")


if __name__ == "__main__":
    main()
