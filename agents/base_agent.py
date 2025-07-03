from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
import asyncio
import json
import logging
from datetime import datetime
from pydantic import BaseModel, Field

import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.prompt_template.prompt_template_config import PromptTemplateConfig

from config.azure_config import config


class AgentMemory(BaseModel):
    """Agent memory structure"""
    short_term: List[Dict[str, Any]] = Field(default_factory=list)
    long_term: Dict[str, Any] = Field(default_factory=dict)
    relationships: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    
    def add_short_term_memory(self, memory: Dict[str, Any]):
        self.short_term.append({
            **memory,
            "timestamp": datetime.utcnow().isoformat()
        })
        # Keep only last 20 memories in short term
        if len(self.short_term) > 20:
            self.short_term = self.short_term[-20:]
    
    def add_relationship(self, agent_id: str, relationship_data: Dict[str, Any]):
        if agent_id not in self.relationships:
            self.relationships[agent_id] = {}
        self.relationships[agent_id].update(relationship_data)


class BaseAgent(ABC):
    """Base class for all AI agents"""
    
    def __init__(
        self,
        agent_id: str,
        name: str,
        personality: Dict[str, Any],
        system_prompt: Optional[str] = None
    ):
        self.agent_id = agent_id
        self.name = name
        self.personality = personality
        self.memory = AgentMemory()
        self.kernel = sk.Kernel()
        self.chat_history = ChatHistory()
        self.logger = logging.getLogger(f"Agent.{self.name}")
        
        # Initialize Azure OpenAI service
        self._setup_kernel()
        
        # Set system prompt
        if system_prompt:
            self.system_prompt = system_prompt
        else:
            self.system_prompt = self._generate_system_prompt()
    
    def _setup_kernel(self):
        """Setup Semantic Kernel with Azure OpenAI"""
        # Add Azure OpenAI chat service
        self.kernel.add_service(
            AzureChatCompletion(
                service_id="chat",
                deployment_name=config.azure_openai_deployment_name,
                endpoint=config.azure_openai_endpoint,
                api_key=config.azure_openai_api_key,
            )
        )
    
    def _generate_system_prompt(self) -> str:
        """Generate system prompt based on personality"""
        personality_str = "\n".join([f"- {k}: {v}" for k, v in self.personality.items()])
        return f"""You are {self.name}, an AI agent with the following personality traits:
{personality_str}

Maintain consistency with these traits in all interactions. Remember previous conversations and relationships with other agents."""
    
    @abstractmethod
    async def process_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Process an incoming message and generate a response"""
        pass
    
    async def think(self, prompt: str) -> str:
        """Internal thinking process using Semantic Kernel"""
        # Create execution settings
        execution_settings = sk.kernel_types.chat_completion.ChatCompletionSettings(
            service_id="chat",
            max_tokens=2000,
            temperature=0.7,
        )
        
        # Add system message to chat history if empty
        if len(self.chat_history.messages) == 0:
            self.chat_history.add_system_message(self.system_prompt)
        
        # Add user message
        self.chat_history.add_user_message(prompt)
        
        # Get response
        response = await self.kernel.invoke_prompt(
            function_name="think",
            plugin_name="agent",
            prompt=prompt,
            settings=execution_settings,
        )
        
        # Add assistant message
        self.chat_history.add_assistant_message(str(response))
        
        return str(response)
    
    def remember(self, event: Dict[str, Any]):
        """Store an event in memory"""
        self.memory.add_short_term_memory(event)
        self.logger.info(f"Agent {self.name} remembered: {event}")
    
    def recall(self, query: str) -> List[Dict[str, Any]]:
        """Recall memories related to a query"""
        # Simple keyword-based recall for now
        relevant_memories = []
        query_lower = query.lower()
        
        for memory in self.memory.short_term:
            memory_str = json.dumps(memory).lower()
            if any(word in memory_str for word in query_lower.split()):
                relevant_memories.append(memory)
        
        return relevant_memories
    
    def update_relationship(self, other_agent_id: str, relationship_data: Dict[str, Any]):
        """Update relationship with another agent"""
        self.memory.add_relationship(other_agent_id, relationship_data)
        self.logger.info(f"Agent {self.name} updated relationship with {other_agent_id}: {relationship_data}")
    
    def get_state(self) -> Dict[str, Any]:
        """Get current agent state for persistence"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "personality": self.personality,
            "memory": self.memory.model_dump(),
            "chat_history": [msg.model_dump() for msg in self.chat_history.messages]
        }
    
    def load_state(self, state: Dict[str, Any]):
        """Load agent state from persistence"""
        self.memory = AgentMemory(**state.get("memory", {}))
        # Restore chat history if needed
        if "chat_history" in state:
            self.chat_history = ChatHistory()
            # Note: You'd need to properly restore the chat history messages here