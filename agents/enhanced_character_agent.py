import json
import os
from typing import Dict, Any
from pathlib import Path

# Semantic Kernel imports
from semantic_kernel import Kernel
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.plugins.core import ConversationSummaryPlugin, TextPlugin

# Your existing imports
from .character_memory import CharacterMemory

class EnhancedCharacterAgent(ChatCompletionAgent):
    """Enhanced character agent using SK Agent Framework"""
    
    def __init__(self, agent_id: str, character_file: str):
        # Store identifiers
        self.agent_id = agent_id
        self.character_data = self._load_character_data(character_file)
        
        # Initialize enhanced memory
        self.memory = CharacterMemory(agent_id)
        
        # Create kernel with Azure OpenAI
        kernel = self._create_kernel()
        
        # Initialize SK Agent Framework
        super().__init__(
            service_id="azure_openai",
            kernel=kernel,
            name=self.character_data["name"],
            instructions=self._build_enhanced_instructions(),
            description=self.character_data.get("description", ""),
        )
        
        # Keep compatibility with your existing code
        self.name = self.character_data["name"]
    
    def _load_character_data(self, character_file: str) -> Dict:
        """Load character data (same as your current implementation)"""
        file_path = Path(character_file)
        if not file_path.exists():
            return {
                "name": "Unknown Character",
                "personality": "A mysterious individual.",
                "background": "Their past is unknown.",
                "speaking_style": "Speaks formally.",
                "expertise": ["General knowledge"],
                "goals": ["Understanding"]
            }
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _create_kernel(self) -> Kernel:
        """Create Semantic Kernel with Azure OpenAI"""
        kernel = Kernel()
        
        # Add Azure OpenAI service
        azure_openai = AzureChatCompletion(
            deployment_name=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"),
            endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            service_id="azure_openai"
        )
        kernel.add_service(azure_openai)
        
        # Add useful plugins
        kernel.add_plugin(ConversationSummaryPlugin(kernel=kernel), "conversation")
        kernel.add_plugin(TextPlugin(), "text")
        
        return kernel
    
    def _build_enhanced_instructions(self) -> str:
        """Build comprehensive character instructions"""
        return f"""
        CHARACTER IDENTITY:
        Name: {self.character_data['name']}
        
        PERSONALITY: {self.character_data.get('personality', '')}
        BACKGROUND: {self.character_data.get('background', '')}
        SPEAKING STYLE: {self.character_data.get('speaking_style', '')}
        EXPERTISE: {', '.join(self.character_data.get('expertise', []))}
        GOALS: {', '.join(self.character_data.get('goals', []))}
        
        BEHAVIORAL GUIDELINES:
        1. Always respond in character, maintaining personality consistency
        2. Reference your background and expertise when relevant
        3. Build upon previous conversations and relationships
        4. Adapt your response style based on communication context
        5. Show growth and learning from interactions
        
        MEMORY AND RELATIONSHIPS:
        - Remember previous conversations and build relationships
        - Acknowledge familiarity levels with other characters
        - Reference shared experiences when appropriate
        - Show emotional intelligence in responses
        """
    
    async def process_message(self, message: str, context: Dict = None) -> str:
        """
        MAIN METHOD: Replace your current process_message with this
        Compatible with your existing TwoAgentConversation code
        """
        context = context or {}
        
        # Enhance message with relationship and context data
        enhanced_message = await self._enhance_message_with_context(message, context)
        
        try:
            # Use SK Agent Framework for intelligent response
            response = await self.invoke_async(enhanced_message)
            
            # Store interaction in memory
            if "from_agent" in context:
                self.memory.remember_interaction(
                    context["from_agent"], 
                    message, 
                    response, 
                    context
                )
            
            return response
            
        except Exception as e:
            # Fallback response
            return f"I apologize, but I'm having difficulty processing that request. As {self.name}, I'd like to help but need a moment to gather my thoughts."
    
    async def _enhance_message_with_context(self, message: str, context: Dict) -> str:
        """Enhance message with relationship and conversation context"""
        enhanced_parts = [message]
        
        # Add relationship context
        if "from_agent" in context:
            relationship_context = self.memory.get_relationship_context(context["from_agent"])
            enhanced_parts.append(f"\n[RELATIONSHIP CONTEXT: {relationship_context}]")
        
        # Add communication pattern context
        comm_pattern = context.get("communication_pattern", "normal")
        if comm_pattern != "normal":
            enhanced_parts.append(f"\n[COMMUNICATION TYPE: {comm_pattern}]")
        
        # Add conversation history
        if "conversation_history" in context and context["conversation_history"]:
            recent_history = context["conversation_history"][-2:]
            history_summary = "\n".join([
                f"- {h.get('speaker', 'Someone')}: {h.get('message', '')[:50]}..." 
                for h in recent_history
            ])
            enhanced_parts.append(f"\n[RECENT CONVERSATION:\n{history_summary}]")
        
        return "\n".join(enhanced_parts)
    
    def get_memory_summary(self) -> Dict:
        """Get agent memory summary"""
        return {
            "character_id": self.agent_id,
            "name": self.name,
            "total_conversations": sum(len(convs) for convs in self.memory.conversations.values()),
            "relationships": {
                agent_id: {
                    "familiarity": rel["familiarity"],
                    "trust_level": rel["trust_level"],
                    "conversation_count": rel["conversation_count"]
                }
                for agent_id, rel in self.memory.relationships.items()
            }
        }