from typing import Dict, List, Any
from datetime import datetime

class CharacterMemory:
    """Enhanced memory system for character agents"""
    
    def __init__(self, character_id: str):
        self.character_id = character_id
        self.conversations: Dict[str, List[Dict]] = {}
        self.relationships: Dict[str, Dict] = {}
        self.personality_traits: Dict[str, float] = {}
        self.learned_facts: List[Dict] = []
        
    def remember_interaction(self, other_agent_id: str, message: str, response: str, context: Dict = None):
        """Store a conversation exchange"""
        if other_agent_id not in self.conversations:
            self.conversations[other_agent_id] = []
            
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "response": response,
            "context": context or {},
            "turn_number": len(self.conversations[other_agent_id]) + 1
        }
        
        self.conversations[other_agent_id].append(interaction)
        self._update_relationship(other_agent_id, interaction)
    
    def _update_relationship(self, other_agent_id: str, interaction: Dict):
        """Update relationship metrics based on interaction"""
        if other_agent_id not in self.relationships:
            self.relationships[other_agent_id] = {
                "trust_level": 5.0,
                "familiarity": 0.0,
                "collaboration_score": 5.0,
                "conversation_count": 0,
                "first_meeting": interaction["timestamp"],
                "last_interaction": interaction["timestamp"],
                "relationship_notes": []
            }
        
        rel = self.relationships[other_agent_id]
        rel["conversation_count"] += 1
        rel["familiarity"] = min(10.0, rel["familiarity"] + 0.5)
        rel["last_interaction"] = interaction["timestamp"]
        
        # Simple engagement scoring
        message_length = len(interaction["message"])
        if message_length > 100:
            rel["collaboration_score"] = min(10.0, rel["collaboration_score"] + 0.2)
    
    def get_relationship_context(self, other_agent_id: str) -> str:
        """Get relationship context for prompt enhancement"""
        if other_agent_id not in self.relationships:
            return "This is a new acquaintance."
        
        rel = self.relationships[other_agent_id]
        recent_conversations = self.conversations.get(other_agent_id, [])[-3:]
        
        context = f"""
        Relationship Context:
        - Familiarity: {rel['familiarity']}/10
        - Trust Level: {rel['trust_level']}/10
        - Conversations: {rel['conversation_count']}
        - Last met: {rel['last_interaction']}
        
        Recent topics: {[conv['message'][:50] + '...' for conv in recent_conversations]}
        """
        
        return context