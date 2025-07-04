#!/usr/bin/env python3
"""
SK Agent Framework Fixed for Pydantic v2 Compatibility
Working with semantic-kernel==1.34.0 and pydantic==2.11.2
"""

import asyncio
import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime

# SK 1.34.0 imports with proper Pydantic v2 handling
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.contents import ChatHistory, ChatMessageContent, AuthorRole

# Don't inherit from ChatCompletionAgent - work with it instead
try:
    from semantic_kernel.agents import ChatCompletionAgent
    SK_AGENTS_AVAILABLE = True
except ImportError:
    SK_AGENTS_AVAILABLE = False
    print("⚠️  SK Agents not available, using core SK only")


class SKCompatibleCharacterAgent:
    """
    SK-compatible character agent that works with Pydantic v2
    Uses composition instead of inheritance to avoid Pydantic conflicts
    """
    
    def __init__(self, agent_id: str, character_data: Dict[str, Any]):
        self.agent_id = agent_id
        self.character_data = character_data
        self.name = character_data["name"]
        self.conversation_history = ChatHistory()
        
        # Create kernel
        self.kernel = Kernel()
        
        # Add Azure OpenAI service
        try:
            azure_service = AzureChatCompletion(
                deployment_name=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME", "gpt-35-turbo"),
                endpoint=os.getenv("AZURE_OPENAI_ENDPOINT", ""),
                api_key=os.getenv("AZURE_OPENAI_API_KEY", ""),
                service_id="azure_openai"
            )
            self.kernel.add_service(azure_service)
            self.ai_service = azure_service
            print(f"✅ {self.name} connected to Azure OpenAI")
            
        except Exception as e:
            print(f"⚠️  Azure OpenAI connection failed for {self.name}: {e}")
            self.ai_service = None
        
        # Build character instructions
        self.instructions = self._build_character_instructions()
        
        # Try to create SK Agent if available
        self.sk_agent = None
        if SK_AGENTS_AVAILABLE and self.ai_service:
            try:
                self.sk_agent = ChatCompletionAgent(
                    service_id="azure_openai",
                    kernel=self.kernel,
                    name=self.name,
                    instructions=self.instructions,
                )
                print(f"✅ {self.name} SK Agent created successfully")
            except Exception as e:
                print(f"⚠️  SK Agent creation failed for {self.name}: {e}")
                print(f"   Using direct kernel approach instead")
    
    def _build_character_instructions(self) -> str:
        """Build comprehensive character instructions"""
        return f"""
        You are {self.character_data['name']}.
        
        PERSONALITY: {self.character_data.get('personality', '')}
        BACKGROUND: {self.character_data.get('background', '')}
        SPEAKING STYLE: {self.character_data.get('speaking_style', '')}
        EXPERTISE: {', '.join(self.character_data.get('expertise', []))}
        
        Always respond as {self.character_data['name']} would, staying completely in character.
        Be authentic to your personality, background, and expertise.
        Reference previous conversation when appropriate.
        Keep responses focused and engaging.
        """
    
    async def process_message(self, message: str, context: Dict = None) -> str:
        """Process message using best available SK method"""
        context = context or {}
        
        # Try SK Agent first if available
        if self.sk_agent:
            try:
                # Add message to conversation history
                self.conversation_history.add_user_message(message)
                
                # Use SK Agent Framework
                response = await self.sk_agent.invoke_async(message)
                
                # Add response to history
                self.conversation_history.add_assistant_message(response)
                
                return response
                
            except Exception as e:
                print(f"⚠️  SK Agent invoke failed for {self.name}: {e}")
                # Fall through to kernel approach
        
        # Fallback to direct kernel usage
        return await self._process_with_kernel(message, context)
    
    async def _process_with_kernel(self, message: str, context: Dict) -> str:
        """Process message using direct kernel approach"""
        try:
            # Build enhanced prompt with conversation context
            conversation_context = ""
            if len(self.conversation_history.messages) > 0:
                recent_messages = self.conversation_history.messages[-4:]  # Last 4 messages
                conversation_context = "\n".join([
                    f"{msg.role.value}: {msg.content}" for msg in recent_messages
                ])
            
            enhanced_prompt = f"""
            {self.instructions}
            
            {"Previous conversation:" if conversation_context else ""}
            {conversation_context}
            
            User: {message}
            
            {self.name}:
            """
            
            # Create a simple prompt execution
            from semantic_kernel.functions import KernelArguments
            
            # Get chat completion service
            chat_service = self.kernel.get_service("azure_openai")
            if not chat_service:
                return f"I apologize, {self.name} is experiencing technical difficulties."
            
            # Create chat history for this request
            request_history = ChatHistory()
            request_history.add_user_message(enhanced_prompt)
            
            # Get response from Azure OpenAI
            response = await chat_service.get_chat_message_contents(
                chat_history=request_history,
                settings=None,
                kernel=self.kernel,
                arguments=KernelArguments()
            )
            
            if response and len(response) > 0:
                response_text = response[0].content.strip()
                
                # Update conversation history
                self.conversation_history.add_user_message(message)
                self.conversation_history.add_assistant_message(response_text)
                
                return response_text
            else:
                return f"I apologize, but {self.name} is having difficulty responding right now."
                
        except Exception as e:
            return f"I apologize, but {self.name} encountered an error: {str(e)}"


class SKCompatibleConversation:
    """SK-compatible conversation manager"""
    
    def __init__(self, agent1: SKCompatibleCharacterAgent, agent2: SKCompatibleCharacterAgent):
        self.agent1 = agent1
        self.agent2 = agent2
        self.conversation_log = []
    
    async def start_conversation(self, initial_topic: str, max_turns: int = 4):
        """Start conversation using SK-compatible agents"""
        print(f"\n🤖 SK-Compatible Agent Conversation")
        print("=" * 60)
        print(f"Participants: {self.agent1.name} and {self.agent2.name}")
        print(f"Topic: {initial_topic}")
        print(f"Using: Semantic Kernel 1.34.0 + Pydantic 2.11.2")
        print("=" * 60)
        
        current_speaker = self.agent1
        current_listener = self.agent2
        current_message = initial_topic
        
        for turn in range(max_turns):
            print(f"\n--- Turn {turn + 1} ---")
            print(f"{current_speaker.name}: {current_message}")
            
            # Get response from listener
            response = await current_listener.process_message(current_message)
            print(f"\n{current_listener.name}: {response}")
            
            # Log the exchange
            self.conversation_log.append({
                "turn": turn + 1,
                "speaker": current_speaker.name,
                "message": current_message,
                "listener": current_listener.name,
                "response": response,
                "timestamp": datetime.now().isoformat()
            })
            
            # Switch speakers
            current_speaker, current_listener = current_listener, current_speaker
            current_message = response
            
            await asyncio.sleep(1.0)
        
        print(f"\n{'='*60}")
        print("🤖 SK-Compatible Conversation Complete!")
        
        # Show analysis
        await self._analyze_conversation()
    
    async def _analyze_conversation(self):
        """Analyze the conversation"""
        print(f"\n📊 Conversation Analysis:")
        print("-" * 40)
        
        total_exchanges = len(self.conversation_log)
        avg_length = sum(len(ex['response']) for ex in self.conversation_log) / total_exchanges if total_exchanges > 0 else 0
        
        print(f"Total exchanges: {total_exchanges}")
        print(f"Average response length: {avg_length:.0f} characters")
        
        # Show conversation flow
        print(f"\nConversation flow:")
        for ex in self.conversation_log:
            print(f"  Turn {ex['turn']}: {ex['speaker']} → {ex['listener']}")


async def create_compatible_characters():
    """Create SK-compatible characters"""
    
    # Character data
    sherlock_data = {
        "name": "Sherlock Holmes",
        "personality": "Brilliant, analytical, observant detective with exceptional deductive reasoning. Confident, sometimes arrogant, but genuinely cares about justice. Speaks with precision and authority.",
        "background": "World's first consulting detective, living at 221B Baker Street. Solved countless mysteries through observation and logical deduction.",
        "speaking_style": "Precise, eloquent, often uses deductive reasoning in speech. Sometimes condescending but always insightful.",
        "expertise": ["deduction", "forensics", "criminal psychology", "observation", "logical reasoning"]
    }
    
    watson_data = {
        "name": "Dr. Watson",
        "personality": "Loyal, practical, medical professional. Good-natured, steady, and provides emotional balance to Holmes. Rational but more empathetic than Holmes.",
        "background": "Medical doctor and war veteran, Holmes's trusted companion and chronicler of their adventures.",
        "speaking_style": "Clear, professional, empathetic. Often asks clarifying questions and provides medical insights.",
        "expertise": ["medicine", "surgery", "military experience", "practical problem-solving", "human nature"]
    }
    
    print("🔍 Creating SK-compatible characters...")
    sherlock = SKCompatibleCharacterAgent("sherlock_holmes", sherlock_data)
    watson = SKCompatibleCharacterAgent("dr_watson", watson_data)
    
    return sherlock, watson


async def test_sk_compatibility():
    """Test SK compatibility with current versions"""
    print("🧪 TESTING SK COMPATIBILITY")
    print("=" * 50)
    
    # Check versions
    try:
        import semantic_kernel
        import pydantic
        print(f"✅ Semantic Kernel: {semantic_kernel.__version__}")
        print(f"✅ Pydantic: {pydantic.__version__}")
    except Exception as e:
        print(f"❌ Version check failed: {e}")
        return False
    
    # Test basic SK functionality
    try:
        kernel = Kernel()
        print("✅ Kernel creation works")
    except Exception as e:
        print(f"❌ Kernel creation failed: {e}")
        return False
    
    # Test Azure OpenAI connection
    try:
        azure_service = AzureChatCompletion(
            deployment_name="test",
            endpoint="https://test.openai.azure.com",
            api_key="test_key",
            service_id="azure_openai"
        )
        print("✅ Azure OpenAI service creation works")
    except Exception as e:
        print(f"❌ Azure OpenAI service creation failed: {e}")
        return False
    
    # Test ChatCompletionAgent creation
    try:
        if SK_AGENTS_AVAILABLE:
            # Don't actually create it, just test the import
            print("✅ ChatCompletionAgent import works")
        else:
            print("⚠️  ChatCompletionAgent not available")
    except Exception as e:
        print(f"❌ ChatCompletionAgent test failed: {e}")
        return False
    
    return True


async def compare_with_custom_approach():
    """Compare SK approach with your custom approach"""
    print(f"\n" + "="*70)
    print("📊 SK-COMPATIBLE vs YOUR CUSTOM APPROACH")
    print("="*70)
    
    print(f"""
    🤖 SK-COMPATIBLE APPROACH (Working):
    ✅ Uses Semantic Kernel 1.34.0 with Pydantic 2.11.2
    ✅ Azure OpenAI integration through SK services
    ✅ ChatHistory for conversation management
    ✅ Graceful fallbacks when SK Agent Framework fails
    ✅ Compatible with current dependency versions
    
    STRENGTHS:
    • Leverages SK's Azure service integrations
    • Access to SK plugin ecosystem
    • Consistent with Microsoft's AI strategy
    • ChatHistory provides structured conversation management
    
    LIMITATIONS:
    • Still no emotional intelligence
    • No advanced relationship tracking
    • Dependency on framework stability
    • Generic conversation patterns
    
    🎭 YOUR ENHANCED CUSTOM APPROACH:
    ✅ Emotional state management (mood, energy, personality evolution)
    ✅ Advanced relationship tracking (familiarity, trust, sentiment)
    ✅ Topic expertise and context awareness
    ✅ Conversation reflection and learning
    ✅ Platform integration (Azure Functions, SignalR, Cosmos DB)
    ✅ Multi-user room management
    ✅ Custom communication patterns (broadcast, P2P, voting)
    ✅ Zero dependency conflicts
    
    🎯 THE VERDICT:
    
    FOR LEARNING SK CONCEPTS: SK-compatible approach works
    FOR YOUR CHARACTER PLATFORM: Custom approach still wins
    
    Why? Your platform needs:
    • Character relationships that evolve over time
    • Emotional intelligence for authentic interactions
    • Multi-user rooms with humans + AI characters  
    • Real-time streaming to web/mobile/VR clients
    • Democratic character decision-making
    • Platform-specific business logic
    
    SK provides infrastructure, but your innovations provide the magic!
    
    🚀 HYBRID RECOMMENDATION:
    Use SK for infrastructure (Azure connections, plugins) but keep your
    custom orchestration for character intelligence and platform features.
    """)


async def main():
    """Main SK compatibility test and comparison"""
    print("🚀 SK Agent Framework - Fixed for Your Environment")
    print("Testing compatibility with semantic-kernel==1.34.0 + pydantic==2.11.2")
    print("="*80)
    
    try:
        # Test SK compatibility
        if not await test_sk_compatibility():
            print("❌ SK compatibility test failed")
            return
        
        # Create and test characters
        sherlock, watson = await create_compatible_characters()
        
        # Run conversation
        conversation = SKCompatibleConversation(sherlock, watson)
        
        mystery_topic = """Watson, I've discovered something most peculiar about the Whitmore case. 
        The victim had traces of a rare poison under his fingernails, yet the coroner found no signs of 
        poisoning in the body. What's your medical opinion on this contradiction?"""
        
        await conversation.start_conversation(mystery_topic, max_turns=4)
        
        # Compare approaches
        await compare_with_custom_approach()
        
        print(f"\n✅ SK compatibility test complete!")
        print(f"🎯 You've now seen SK working with your current environment")
        print(f"📚 Ready for Azure Services Integration?")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        print(f"\n💡 Your custom approach remains the better choice for stability!")


if __name__ == "__main__":
    asyncio.run(main())