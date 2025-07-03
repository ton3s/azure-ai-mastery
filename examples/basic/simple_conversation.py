import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.character_agent import CharacterAgent


async def simple_sherlock_conversation():
    """Simple conversation with Sherlock Holmes"""
    print("Creating Sherlock Holmes agent...")
    
    # Create Sherlock Holmes agent
    sherlock = CharacterAgent(
        agent_id="sherlock_001",
        character_file="characters/sherlock_holmes.json"
    )
    
    print(f"\nAgent created: {sherlock.name}")
    print("-" * 50)
    
    # Get introduction
    print("\n[Getting introduction...]")
    introduction = await sherlock.introduce_self()
    print(f"\nSherlock: {introduction}")
    
    # Have a conversation
    print("\n" + "-" * 50)
    print("Starting conversation...\n")
    
    # Simulate a conversation
    user_messages = [
        "Good morning, Mr. Holmes. I need your help with a puzzling case.",
        "My neighbor's prized orchid has vanished from their locked greenhouse. No signs of forced entry.",
        "The only unusual thing was a faint smell of pipe tobacco, though my neighbor doesn't smoke.",
        "What should I look for next?"
    ]
    
    for message in user_messages:
        print(f"You: {message}")
        response = await sherlock.process_message(message)
        print(f"\nSherlock: {response}\n")
        print("-" * 30 + "\n")
        
        # Small delay to simulate natural conversation
        await asyncio.sleep(0.5)
    
    # Show agent's memory
    print("\n[Agent's Short-term Memory]")
    for i, memory in enumerate(sherlock.memory.short_term[-3:], 1):
        print(f"{i}. {memory['type']}: {memory['message'][:100]}...")


async def main():
    """Run the example"""
    print("Simple Sherlock Holmes Conversation Example")
    print("=" * 50)
    
    try:
        await simple_sherlock_conversation()
        print("\n✅ Example completed successfully!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure you have:")
        print("1. Created a .env file with your Azure OpenAI credentials")
        print("2. Installed all dependencies: pip install -r requirements.txt")


if __name__ == "__main__":
    asyncio.run(main())