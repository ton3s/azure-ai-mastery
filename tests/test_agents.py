import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.character_agent import CharacterAgent
from config.azure_config import config


async def test_character_agent_creation():
    """Test creating a character agent"""
    print("Testing character agent creation...")
    
    try:
        # Create Sherlock Holmes agent
        sherlock = CharacterAgent(
            agent_id="sherlock_001",
            character_file="characters/sherlock_holmes.json"
        )
        
        print(f"✓ Created agent: {sherlock.name}")
        print(f"✓ Agent ID: {sherlock.agent_id}")
        
        # Get character info
        info = sherlock.get_character_info()
        print(f"✓ Personality traits: {len(info['personality'])} defined")
        print(f"✓ Knowledge areas: {len(info['knowledge_areas'])} defined")
        
        return sherlock
        
    except Exception as e:
        print(f"✗ Failed to create character agent: {e}")
        return None


async def test_character_introduction(agent):
    """Test character introduction"""
    print("\nTesting character introduction...")
    
    try:
        introduction = await agent.introduce_self()
        print(f"✓ Character introduction:\n{introduction}")
        return True
    except Exception as e:
        print(f"✗ Failed to get introduction: {e}")
        return False


async def test_character_conversation(agent):
    """Test character conversation"""
    print("\nTesting character conversation...")
    
    messages = [
        "Holmes, I've found a mysterious letter at the crime scene.",
        "What do you make of this tobacco ash I found?",
        "The victim was last seen at the train station at midnight."
    ]
    
    try:
        for message in messages:
            print(f"\nUser: {message}")
            response = await agent.process_message(message)
            print(f"Sherlock: {response}")
        
        return True
    except Exception as e:
        print(f"✗ Conversation test failed: {e}")
        return False


async def test_character_memory(agent):
    """Test character memory"""
    print("\nTesting character memory...")
    
    try:
        # Add some memories
        agent.remember({"type": "clue", "content": "Found a blue fiber"})
        agent.remember({"type": "suspect", "content": "Professor Moriarty mentioned"})
        
        # Recall memories
        memories = agent.recall("fiber")
        print(f"✓ Recalled {len(memories)} memories about 'fiber'")
        
        memories = agent.recall("Moriarty")
        print(f"✓ Recalled {len(memories)} memories about 'Moriarty'")
        
        return True
    except Exception as e:
        print(f"✗ Memory test failed: {e}")
        return False


async def test_character_situation_reaction(agent):
    """Test character reaction to situations"""
    print("\nTesting character reactions...")
    
    situations = [
        "You discover that someone has been in your apartment while you were away.",
        "A new client arrives claiming their priceless painting has been stolen.",
        "Watson suggests taking a holiday to the countryside."
    ]
    
    try:
        for situation in situations:
            print(f"\nSituation: {situation}")
            reaction = await agent.react_to_situation(situation)
            print(f"Sherlock's reaction: {reaction}")
        
        return True
    except Exception as e:
        print(f"✗ Situation reaction test failed: {e}")
        return False


async def main():
    """Run all agent tests"""
    print("Character Agent Tests")
    print("=" * 50)
    
    # Create agent
    agent = await test_character_agent_creation()
    if not agent:
        print("\n❌ Failed to create agent. Cannot continue tests.")
        return
    
    # Run tests
    tests = [
        test_character_introduction,
        test_character_conversation,
        test_character_memory,
        test_character_situation_reaction
    ]
    
    all_passed = True
    for test in tests:
        if not await test(agent):
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ All agent tests passed!")
    else:
        print("❌ Some agent tests failed.")


if __name__ == "__main__":
    # Check if .env exists
    env_path = Path(__file__).parent.parent / ".env"
    if not env_path.exists():
        print("⚠️  .env file not found. Please create it from .env.example")
        print("   and add your Azure OpenAI credentials.")
        sys.exit(1)
    
    asyncio.run(main())