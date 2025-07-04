import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.character_agent import CharacterAgent
from agents.enhanced_character_agent import EnhancedCharacterAgent


class TwoAgentConversation:
    """Manages conversation between two AI agents"""
    
    def __init__(self, agent1: CharacterAgent, agent2: CharacterAgent):
        self.agent1 = agent1
        self.agent2 = agent2
        self.conversation_history = []
        self.turn_count = 0
    
    async def start_conversation(self, initial_topic: str, max_turns: int = 6):
        """Start a conversation between the two agents"""
        agent1_name = getattr(self.agent1, 'display_name', self.agent1.name)
        agent2_name = getattr(self.agent2, 'display_name', self.agent2.name)
        print(f"\n🎭 Conversation between {agent1_name} and {agent2_name}")
        print("=" * 60)
        print(f"Topic: {initial_topic}")
        print("=" * 60)
        
        # Agent 1 starts the conversation
        current_speaker = self.agent1
        current_listener = self.agent2
        current_message = initial_topic
        
        for turn in range(max_turns):
            self.turn_count += 1
            
            print(f"\n--- Turn {self.turn_count} ---")
            speaker_name = getattr(current_speaker, 'display_name', current_speaker.name)
            print(f"{speaker_name}: {current_message}")
            
            # Process the message and get response
            response = await current_listener.process_message(
                current_message,
                context={
                    "from_agent": current_speaker.agent_id,
                    "conversation_turn": self.turn_count,
                    "conversation_history": self.conversation_history[-3:]  # Last 3 exchanges
                }
            )
            
            listener_name = getattr(current_listener, 'display_name', current_listener.name)
            # print(f"\n{listener_name}: {response}")
            
            # Record this exchange
            self.conversation_history.append({
                "turn": self.turn_count,
                "speaker": speaker_name,
                "listener": listener_name,
                "message": current_message,
                "response": response,
                "timestamp": asyncio.get_event_loop().time()
            })
            
            # Switch speakers for next turn
            current_speaker, current_listener = current_listener, current_speaker
            current_message = response
            
            # Small delay for readability
            await asyncio.sleep(0.8)
        
        print(f"\n{'='*60}")
        print("🏁 Conversation completed!")
        
        # Show relationship development
        await self._show_relationship_development()
    
    async def _show_relationship_development(self):
        """Show how the agents' relationships have developed"""
        print(f"\n🤝 Relationship Development:")
        print("-" * 40)
        
        # Check agent1's view of agent2
        agent1_name = getattr(self.agent1, 'display_name', self.agent1.name)
        agent2_name = getattr(self.agent2, 'display_name', self.agent2.name)
        
        # Check agent1's relationships
        if hasattr(self.agent1, 'memory'):
            agent1_relationship = self.agent1.memory.relationships.get(self.agent2.agent_id, {})
            print(f"{agent1_name}'s view of {agent2_name}:")
            for key, value in agent1_relationship.items():
                print(f"  • {key}: {value}")
        
        print()
        
        # Check agent2's relationships (enhanced agent)
        if hasattr(self.agent2, 'enhanced_relationships'):
            agent2_enhanced = self.agent2.enhanced_relationships.get(self.agent1.agent_id, {})
            agent2_base = self.agent2.memory.relationships.get(self.agent1.agent_id, {})
            print(f"{agent2_name}'s view of {agent1_name}:")
            print("  Base relationship:")
            for key, value in agent2_base.items():
                print(f"    • {key}: {value}")
            print("  Enhanced relationship:")
            for key, value in agent2_enhanced.items():
                if key == "emotional_impact":
                    print(f"    • {key}: {value[-3:]}")  # Last 3 emotions
                else:
                    print(f"    • {key}: {value}")
    
    def get_conversation_summary(self) -> str:
        """Get a summary of the conversation"""
        if not self.conversation_history:
            return "No conversation has taken place."
        
        summary = f"Conversation Summary ({len(self.conversation_history)} exchanges):\n"
        for exchange in self.conversation_history:
            summary += f"Turn {exchange['turn']}: {exchange['speaker']} → {exchange['listener']}\n"
        
        return summary


async def demonstrate_two_agent_conversation():
    """Demonstrate a conversation between Sherlock Holmes and Dr. Watson"""
    
    print("🔍 Creating Sherlock Holmes...")
    sherlock = EnhancedCharacterAgent(
        agent_id="sherlock_holmes",
        character_file="characters/sherlock_holmes.json"
    )
    
    print("🩺 Creating Dr. Watson...")
    watson = EnhancedCharacterAgent(
        agent_id="dr_watson", 
        character_file="characters/dr_watson.json"
    )
    
    print(f"\n✅ Both agents created successfully!")
    print(f"Sherlock: {sherlock.name}")
    print(f"Watson: {watson.display_name}")
    
    # Create conversation manager
    conversation = TwoAgentConversation(sherlock, watson)
    
    # Start a mystery discussion
    mystery_topic = "Watson, I've discovered something most peculiar about the Whitmore case. The victim had traces of a rare poison under his fingernails, yet the coroner found no signs of poisoning in the body. What's your medical opinion on this contradiction?"
    
    await conversation.start_conversation(mystery_topic, max_turns=6)
    
    # Show conversation summary
    print(f"\n📊 {conversation.get_conversation_summary()}")


async def main():
    """Main function to run the demonstration"""
    print("🎭 Two-Agent Conversation System")
    print("=" * 50)
    
    try:
        await demonstrate_two_agent_conversation()
        print("\n✅ Two-agent conversation completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
