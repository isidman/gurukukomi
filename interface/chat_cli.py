"""
GRKKMAI Chat Interface - Command-line Version
"""

import os
import sys
import json
from datetime import datetime

#Adding parent dir so modules can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.ai_brain import GRKKMAI
from core.memory_system import GRKKMAI_MEMORY
from core.personality import GRKKMAIPersonality

class GRKKMCLI:
    def __init__(self):
        print("Starting up Gurukukomi Chat Interface...")
        print("="*50)

        try:
            #Full system initialization
            self.ai = GRKKMAI()
            print(" AI Brain active.")

            #Add memory system if available
            try:
                self.ai.memory = GRKKMAI_MEMORY()
                print("Memory ready.")
            except Exception as e:
                print(f"Memory system not available: {e}")
                self.ai.memory = None

            #Add personality engine if available
            try:
                self.ai.personality = GRKKMAIPersonality()
                print("Personality engine is good to go.")
            except Exception as e:
                print(f"Personality engine not available: {e}")
                self.ai.personality = None

            print("="*50)
            print("Gurukukomi is ready for interaction!")
            print()

        except Exception as e:
            print(f"Error initializing Gurukukomi: {e}")
            sys.exit(1)
    
    def start_chat(self):
        """Start the main chat loop"""
        self.print_welcome()

        while True:
            try:
                user_input = input("\n You: ").strip()

                if self.handle_special_commands(user_input):
                    continue

                if not user_input:
                    continue

                print("\n Gurukukomi: ", end="", flush=True)
                response = self.ai.think(user_input)
                print(response)

            except KeyboardInterrupt:
                print("\n\n Goodbye! Thanks for chatting with Gurukukomi!")
                break
            except EOFError:
                print("\n\n Chat ended. Bye,bye!")
                break
            except Exception as e:
                print(f"\n Error: {e}")
                print("Let's keep chatting though!")

    def handle_special_commands(self, user_input):
        """Handle special chat commands"""
        command = user_input.lower().strip()

        #Help
        if command in ["/help", "help", "commands"]:
            self.print_help()
            return True
        
        #Quit
        elif command in["/quit","/exit","quit","exit","goodbye","bye"]:
            print ("\n Goodbye! Thanks for chatting with Gurukukomi!")
            sys.exit(0)
        
        #Stats
        elif command in ["/stats","stats","statistics"]:
            self.print_stats()
            return True

        #Memory
        elif command in ["/memory","memory","what do you remember"]:
            self.print_memory_info()
            return True

        #Clear
        elif command in ["/clear", "clear"]:
            os.system('clear' if os.name == 'posix' else 'cls')
            self.print_welcome()
            return True

        return False
    
    def print_welcome(self):
        """Print welcome message"""
        print("\n GRKKM-AI Interface")
        print("="*30)
        print("You can just start typing and press Enter when you want to send something over.")
        print("Type '/help' for special commands")
        print("Type '/quit' to exit")
        print("-"*30)

    def print_help(self):
        
        print("\n AVAILABLE COMMANDS:")
        print("-"*30)
        print("/help    - Showing this command's result")
        print("/quit    - Exiting the chat")
        print("/stats   - Showing conversation stats")
        print("/memory  - Showing what I remember")
        print("/personality - Showing my current 'mood'")
        print("/clear   - Clear the screen")
        print("-"*30)

    def print_stats(self):
        
        print("\n CONVERSATION STATS:")
        print("-"*30)

        #Basic convos
        if hasattr(self.ai, 'conversation_history'):
            total_exchanges = len([msg for msg in self.ai.conversation_history if "user" in msg])
            print(f"Total Convos: {total_exchanges}")

        #Memories
        if self.ai.memory:
            try:
                memory_stats = self.ai.memory.get_memory_stats()
                print(f"Memories stored: {memory_stats.get('memories_stored', 0)}")
                print(f"Conversations today: {memory_stats.get('conversations_today', 0)}")
            except:
                print("Memories are not available.")

        #Personality stats
        if self.ai.personality:
            try:
                personality_summary = self.ai.personality.get_personality_summary()
                dominant_traits = personality_summary.get('dominant_traits', [])
                print(f"Top personality traits: {','.join(dominant_traits[:3])}")
            except:
                print("Personality stats are not available.")

            print("-"*30)

    def print_memory_info(self):
        print("MEMORY INFO:")
        print("-"*30)

        if not self.ai.memory:
            print("Memory system not available at the moment.")
            return
        
        try:
            memories = self.ai.memory.get_explicit_memories()
            if not memories:
                print(" No memories stored yet! ")
                print(" I only remember you explicitly want me to remember.")
            else:
                print(f"I remember {len(memories)} things about you:")
                for memory in memories[-5:]: # latest 5 memories 
                    print(f" • {memory ['key']}: {memory['value']}")
                if len(memories) > 5:
                    print(f" ... and {len(memories) - 5} more things")
        except Exception as e:
            print(f"Error accessing memories: {e}")

        print("-"*30)

    def print_personality_info(self):
        print("\n PERSONALITY INFO:")
        print("-"*30)

        if not self.ai.personality:
            print(" Personality engine not available")
            return
        
        try:
            summary = self.ai.personality.get_personality_summary()
            
            print(f" Current mood: {summary.get('mood','Unknown')}")
            print("Top traits:")

            traits = summary.get('traits', {})
            for trait_name, trait_value in list(traits.items())[:3]:
                percentage = int(trait_value * 100)
                print(f" • {trait_name.title()}: {percentage}%")
            
            evolution_events = summary.get('evolution_events', 0)
            print(f"Personality has evolved {evolution_events} times")
        
        except Exception as e:
            print(f"Error accessing personality: {e}")

        print("-"*30)

def main():
    print("DEBUG: Starting GRKKMAI CLI")
    try:
        cli = GRKKMCLI()
        cli.start_chat()
    except Exception as e:
        print(f" Failed to start Gurukukomi: {e}")
        print("Make sure all core modules are properly set up!")
if __name__ == "__main__":

    main()
