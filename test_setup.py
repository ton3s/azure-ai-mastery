#!/usr/bin/env python3
"""Quick test script to verify Azure AI + Semantic Kernel setup"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from config.azure_config import config


async def test_azure_openai():
    """Test Azure OpenAI connection via Semantic Kernel"""
    print("Testing Azure OpenAI connection via Semantic Kernel...")
    
    try:
        import semantic_kernel as sk
        from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
        from semantic_kernel.contents.chat_history import ChatHistory
        
        # Create kernel
        kernel = sk.Kernel()
        
        # Add Azure OpenAI service
        chat_service = AzureChatCompletion(
            service_id="chat",
            deployment_name=config.azure_openai_deployment_name,
            endpoint=config.azure_openai_endpoint,
            api_key=config.azure_openai_api_key,
        )
        kernel.add_service(chat_service)
        
        # Create chat history
        chat_history = ChatHistory()
        chat_history.add_system_message("You are a helpful assistant.")
        chat_history.add_user_message("Say 'Hello, Semantic Kernel + Azure AI is working!' if you can read this.")
        
        # Create execution settings
        settings = chat_service.instantiate_prompt_execution_settings(
            service_id="chat",
            max_tokens=50
        )
        
        # Get response
        response = await chat_service.complete_chat(
            chat_history=chat_history,
            settings=settings
        )
        
        if response and len(response) > 0:
            print(f"✓ Azure OpenAI (via SK) responded: {response[0].content}")
            return True
        else:
            print("✗ No response received from Azure OpenAI")
            return False
        
    except Exception as e:
        print(f"✗ Azure OpenAI test failed: {e}")
        return False


async def test_character_agent():
    """Test character agent creation and response"""
    print("\nTesting Character Agent...")
    
    try:
        from agents.character_agent import CharacterAgent
        
        # Create a simple test agent
        test_agent = CharacterAgent(
            agent_id="test_001",
            character_data={
                "name": "Test Agent",
                "personality": {"helpful": "Always eager to help", "friendly": "Warm and welcoming"},
                "backstory": "I am a test agent created to verify the system works.",
                "traits": ["helpful", "friendly"],
                "speech_patterns": ["I'm happy to help!"],
                "knowledge_areas": ["testing", "verification"]
            }
        )
        
        response = await test_agent.process_message("Hello, are you working?")
        print(f"✓ Agent responded: {response[:100]}...")
        return True
        
    except Exception as e:
        print(f"✗ Character agent test failed: {e}")
        return False


async def main():
    """Run all tests"""
    print("Azure AI + Semantic Kernel Setup Test")
    print("=" * 50)
    
    # Check configuration
    print("Configuration:")
    print(f"- Endpoint: {config.azure_openai_endpoint}")
    print(f"- Deployment: {config.azure_openai_deployment_name}")
    print(f"- API Key: {'*' * 8}...")
    
    # Run tests
    all_passed = True
    
    if not await test_azure_openai():
        all_passed = False
    
    if not await test_character_agent():
        all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ All tests passed! Your setup is working correctly.")
        print("\nNext steps:")
        print("1. Try the Sherlock Holmes example: python examples/basic/simple_conversation.py")
        print("2. Create your own character agents in the characters/ directory")
        print("3. Build multi-agent conversation scenarios")
    else:
        print("❌ Some tests failed. Please check:")
        print("1. Your .env file has the correct Azure OpenAI credentials")
        print("2. Your Azure OpenAI deployment is active and accessible")
        print("3. All dependencies are installed: pip install -r requirements.txt")


if __name__ == "__main__":
    asyncio.run(main())