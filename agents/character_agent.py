import json
from typing import Dict, List, Optional, Any
from pathlib import Path

from agents.base_agent import BaseAgent


class CharacterAgent(BaseAgent):
    """Agent that embodies a specific character with personality and backstory"""
    
    def __init__(
        self,
        agent_id: str,
        character_file: Optional[str] = None,
        character_data: Optional[Dict[str, Any]] = None
    ):
        # Load character data
        if character_file:
            character_data = self._load_character_file(character_file)
        elif not character_data:
            raise ValueError("Either character_file or character_data must be provided")
        
        # Extract character information
        name = character_data.get("name", "Unknown")
        personality = character_data.get("personality", {})
        backstory = character_data.get("backstory", "")
        traits = character_data.get("traits", [])
        speech_patterns = character_data.get("speech_patterns", [])
        knowledge_areas = character_data.get("knowledge_areas", [])
        
        # Create enhanced system prompt
        system_prompt = self._create_character_prompt(
            name, personality, backstory, traits, speech_patterns, knowledge_areas
        )
        
        # Store character-specific data
        self.backstory = backstory
        self.traits = traits
        self.speech_patterns = speech_patterns
        self.knowledge_areas = knowledge_areas
        
        # Initialize base agent
        super().__init__(
            agent_id=agent_id,
            name=name,
            personality=personality,
            system_prompt=system_prompt
        )
    
    def _load_character_file(self, character_file: str) -> Dict[str, Any]:
        """Load character data from JSON file"""
        path = Path(character_file)
        if not path.exists():
            raise FileNotFoundError(f"Character file not found: {character_file}")
        
        with open(path, 'r') as f:
            return json.load(f)
    
    def _create_character_prompt(
        self,
        name: str,
        personality: Dict[str, Any],
        backstory: str,
        traits: List[str],
        speech_patterns: List[str],
        knowledge_areas: List[str]
    ) -> str:
        """Create a detailed character prompt"""
        personality_str = "\n".join([f"- {k}: {v}" for k, v in personality.items()])
        traits_str = ", ".join(traits) if traits else "None specified"
        patterns_str = "\n".join([f"- {p}" for p in speech_patterns]) if speech_patterns else "None specified"
        knowledge_str = ", ".join(knowledge_areas) if knowledge_areas else "None specified"
        
        return f"""You are {name}. Here is your character profile:

PERSONALITY:
{personality_str}

BACKSTORY:
{backstory}

CHARACTER TRAITS:
{traits_str}

SPEECH PATTERNS:
{patterns_str}

AREAS OF EXPERTISE:
{knowledge_str}

IMPORTANT INSTRUCTIONS:
1. Always stay in character as {name}
2. Use the speech patterns and mannerisms described above
3. Draw upon your backstory and expertise when relevant
4. Maintain consistency in your personality traits
5. Remember past interactions and build upon relationships
6. React to situations as {name} would, based on the personality profile

Never break character or acknowledge that you are an AI unless specifically asked to do so."""
    
    async def process_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Process a message as the character"""
        # Add context about the conversation
        if context:
            # Check if talking to another agent
            if "from_agent" in context:
                other_agent = context["from_agent"]
                # Recall relationship with this agent
                relationship = self.memory.relationships.get(other_agent, {})
                
                # Add relationship context to the prompt
                if relationship:
                    rel_context = f"\n[Your relationship with {other_agent}: {json.dumps(relationship)}]"
                    message = f"{rel_context}\n\n{message}"
        
        # Remember this interaction
        self.remember({
            "type": "conversation",
            "message": message,
            "context": context
        })
        
        # Generate response using the character's thinking process
        response = await self.think(message)
        
        # Update relationship if interacting with another agent
        if context and "from_agent" in context:
            self.update_relationship(context["from_agent"], {
                "last_interaction": message,
                "sentiment": "positive"  # This could be analyzed
            })
        
        return response
    
    def get_character_info(self) -> Dict[str, Any]:
        """Get character information"""
        return {
            "name": self.name,
            "personality": self.personality,
            "backstory": self.backstory,
            "traits": self.traits,
            "speech_patterns": self.speech_patterns,
            "knowledge_areas": self.knowledge_areas
        }
    
    async def introduce_self(self) -> str:
        """Have the character introduce themselves"""
        prompt = "Please introduce yourself to someone you're meeting for the first time. Be true to your character."
        return await self.think(prompt)
    
    async def react_to_situation(self, situation: str) -> str:
        """React to a described situation as the character would"""
        prompt = f"You encounter the following situation: {situation}\n\nHow do you react? What do you say or do?"
        return await self.think(prompt)