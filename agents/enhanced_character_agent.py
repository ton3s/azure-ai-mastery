import json
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging

from agents.character_agent import CharacterAgent


class EnhancedCharacterAgent(CharacterAgent):
    """Enhanced character agent with additional capabilities
    
    This version extends CharacterAgent (not SK's ChatCompletionAgent)
    to avoid Pydantic conflicts while still using SK internally.
    """
    
    def __init__(
        self,
        agent_id: str,
        character_file: Optional[str] = None,
        character_data: Optional[Dict[str, Any]] = None
    ):
        # Initialize base character agent
        super().__init__(agent_id, character_file, character_data)
        
        # Enhanced features
        self.conversation_styles = self._extract_conversation_styles()
        self.emotional_state = {"mood": "neutral", "energy": 100}
        self.topic_expertise = self._extract_topic_expertise()
        self.display_name = self.name  # For compatibility
        
        # Create separate enhanced memory storage
        self.emotional_states = []
        self.enhanced_relationships = {}
        
    def _extract_conversation_styles(self) -> Dict[str, Any]:
        """Extract conversation styles from character data"""
        return {
            "formal": self.personality.get("formality", "medium"),
            "humor": self.personality.get("humor", "moderate"),
            "verbosity": self.personality.get("verbosity", "balanced"),
            "empathy": self.personality.get("empathy", "normal")
        }
    
    def _extract_topic_expertise(self) -> Dict[str, float]:
        """Create a topic expertise map from knowledge areas"""
        expertise = {}
        for area in self.knowledge_areas:
            expertise[area.lower()] = 0.9  # High expertise in defined areas
        return expertise
    
    async def process_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Enhanced message processing with emotional awareness and SK integration"""
        # Update emotional state based on conversation
        self._update_emotional_state(message, context)
        
        # Build enhanced prompt with emotional and contextual information
        enhanced_message = self._build_enhanced_message(message, context)
        
        # Use the parent class method which uses SK internally
        response = await super().process_message(enhanced_message, context)
        
        # Update memory and relationships
        self._update_memory(message, response, context)
        
        # Apply conversation style adjustments
        response = self._apply_conversation_style(response, context)
        
        return response
    
    def _build_enhanced_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Build an enhanced message with emotional and contextual information"""
        message_parts = [message]
        
        # Add emotional context
        message_parts.append(f"\n[Your current mood is {self.emotional_state['mood']} with energy level {self.emotional_state['energy']}%]")
        
        # Check if this is a topic we have expertise in
        if self._check_topic_expertise(message):
            message_parts.append("\n[You are highly knowledgeable about this topic]")
        
        # Add relationship context if available
        if context and "from_agent" in context:
            # Check both base relationships and enhanced relationships
            base_rel = self.memory.relationships.get(context["from_agent"], {})
            enhanced_rel = self.enhanced_relationships.get(context["from_agent"], {})
            relationship = {**base_rel, **enhanced_rel}  # Merge both
            if relationship:
                message_parts.append(f"\n[Your relationship with {context['from_agent']}: {json.dumps(relationship)}]")
        
        return "\n".join(message_parts)
    
    def _update_emotional_state(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Update emotional state based on conversation"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["wonderful", "excellent", "brilliant", "fascinating"]):
            self.emotional_state["mood"] = "excited"
            self.emotional_state["energy"] = min(100, self.emotional_state["energy"] + 10)
        elif any(word in message_lower for word in ["difficult", "problem", "concern", "worry"]):
            self.emotional_state["mood"] = "concerned"
            self.emotional_state["energy"] = max(0, self.emotional_state["energy"] - 5)
        elif any(word in message_lower for word in ["thank", "appreciate", "grateful"]):
            self.emotional_state["mood"] = "pleased"
        
        # Energy naturally decreases over long conversations
        if context and "conversation_turn" in context:
            self.emotional_state["energy"] = max(50, 100 - (context["conversation_turn"] * 5))
    
    def _check_topic_expertise(self, message: str) -> bool:
        """Check if the message relates to our areas of expertise"""
        message_lower = message.lower()
        for topic, confidence in self.topic_expertise.items():
            if topic in message_lower and confidence > 0.7:
                return True
        return False
    
    def _apply_conversation_style(self, response: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Apply conversation style adjustments to response"""
        # In a full implementation, this could modify the response based on:
        # - Formality level
        # - Humor settings
        # - Verbosity preferences
        # - Empathy requirements
        return response
    
    def _update_memory(self, message: str, response: str, context: Optional[Dict[str, Any]] = None):
        """Update agent memory with interaction"""
        # Add to short-term memory with emotional state
        self.remember({
            "type": "conversation",
            "message": message,
            "response": response,
            "emotional_state": self.emotional_state.copy()
        })
        
        # Store emotional states
        self.emotional_states.append(self.emotional_state.copy())
        if len(self.emotional_states) > 20:
            self.emotional_states = self.emotional_states[-20:]
        
        # Update enhanced relationships
        if context and "from_agent" in context:
            agent_id = context["from_agent"]
            if agent_id not in self.enhanced_relationships:
                self.enhanced_relationships[agent_id] = {
                    "interaction_count": 0,
                    "sentiment": "neutral",
                    "emotional_impact": []
                }
            
            self.enhanced_relationships[agent_id]["interaction_count"] += 1
            self.enhanced_relationships[agent_id]["emotional_impact"].append(self.emotional_state["mood"])
            
            # Simple sentiment analysis
            sentiment = "neutral"
            if any(word in message.lower() for word in ["thank", "appreciate", "wonderful", "excellent"]):
                sentiment = "positive"
            elif any(word in message.lower() for word in ["problem", "issue", "concern", "upset"]):
                sentiment = "concerned"
            
            self.enhanced_relationships[agent_id]["sentiment"] = sentiment
            
            # Also update the base class memory's relationships
            self.update_relationship(agent_id, {
                "last_interaction": message,
                "sentiment": sentiment
            })
    
    async def reflect_on_conversation(self, conversation_history: List[Dict[str, Any]]) -> str:
        """Reflect on a completed conversation"""
        # Build a summary of the conversation
        summary_prompt = f"""As {self.name}, reflect on this conversation you just had:

{self._format_conversation_history(conversation_history)}

Provide a brief reflection on:
1. What you learned from this interaction
2. How you feel about the other participant
3. Any insights or conclusions you've drawn

Stay in character and respond as {self.name} would."""
        
        reflection = await self.think(summary_prompt)
        
        # Store the reflection as a long-term memory
        self.memory.long_term["last_reflection"] = {
            "content": reflection,
            "conversation_length": len(conversation_history),
            "emotional_journey": self.emotional_states[-5:]
        }
        
        return reflection
    
    def _format_conversation_history(self, history: List[Dict[str, Any]]) -> str:
        """Format conversation history for reflection"""
        formatted = []
        for exchange in history[-5:]:  # Last 5 exchanges
            formatted.append(f"{exchange.get('speaker', 'Unknown')}: {exchange.get('message', '')}")
            if 'response' in exchange:
                formatted.append(f"{exchange.get('listener', 'Unknown')}: {exchange.get('response', '')}")
        return "\n".join(formatted)
    
    def get_emotional_state(self) -> Dict[str, Any]:
        """Get current emotional state"""
        return self.emotional_state.copy()
    
    def reset_emotional_state(self):
        """Reset emotional state to default"""
        self.emotional_state = {"mood": "neutral", "energy": 100}
    
    def get_memory_summary(self) -> Dict[str, Any]:
        """Get agent memory summary"""
        return {
            "character_id": self.agent_id,
            "name": self.name,
            "emotional_state": self.emotional_state,
            "total_memories": len(self.memory.short_term),
            "relationships": {
                agent_id: {
                    "interaction_count": rel.get("interaction_count", 0),
                    "sentiment": rel.get("sentiment", "neutral"),
                    "emotional_impact": rel.get("emotional_impact", [])[-3:] if "emotional_impact" in rel else []
                }
                for agent_id, rel in self.enhanced_relationships.items()
            }
        }
    
