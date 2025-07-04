import asyncio
import sys
from pathlib import Path
import json
import re
from typing import Dict, Any, Optional, Tuple, List

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.character_agent import CharacterAgent


class CharacterDrivenConversation:
    """Manages conversation between two AI agents using character-driven endings"""
    
    def __init__(self, agent1: CharacterAgent, agent2: CharacterAgent):
        self.agent1 = agent1
        self.agent2 = agent2
        self.conversation_history = []
        self.turn_count = 0
        self.max_turns = 20  # Safety limit only
    
    async def start_natural_conversation(self, initial_topic: str):
        """Start a conversation that ends naturally based on character decisions"""
        print(f"\n🎭 Natural Conversation: {self.agent1.name} & {self.agent2.name}")
        print("=" * 60)
        print(f"Topic: {initial_topic}")
        print("💭 Characters will determine when to end naturally...")
        print("=" * 60)
        
        # Agent 1 starts the conversation
        current_speaker = self.agent1
        current_listener = self.agent2
        current_message = initial_topic
        ending_reason = "max_turns_reached"
        
        while self.turn_count < self.max_turns:
            self.turn_count += 1
            
            print(f"\n--- Turn {self.turn_count} ---")
            print(f"{current_speaker.name}: {current_message}")
            
            # Get intelligent response with ending decision
            response_data = await self._get_intelligent_response(
                current_listener, current_message, current_speaker
            )
            
            response = response_data["response"]
            wants_to_end = response_data["wants_to_end"]
            ending_reasoning = response_data["reasoning"]
            confidence = response_data["confidence"]
            
            print(f"\n{current_listener.name}: {response}")
            
            # Record this exchange
            self.conversation_history.append({
                "turn": self.turn_count,
                "speaker": current_speaker.name,
                "listener": current_listener.name,
                "message": current_message,
                "response": response,
                "wants_to_end": wants_to_end,
                "ending_reasoning": ending_reasoning,
                "confidence": confidence,
                "timestamp": asyncio.get_event_loop().time()
            })
            
            # Check if character wants to end
            if wants_to_end:
                print(f"\n💭 {current_listener.name}'s reasoning: {ending_reasoning}")
                print(f"   Confidence: {confidence}/10")
                
                # High confidence = end immediately
                if confidence >= 7:
                    ending_reason = f"character_decision: {ending_reasoning}"
                    print(f"\n🏁 {current_listener.name} chose to end the conversation")
                    break
                
                # Medium confidence = get other character's opinion
                elif confidence >= 4:
                    other_agent_decision = await self._get_ending_consensus(
                        current_speaker, response, ending_reasoning
                    )
                    
                    if other_agent_decision["agrees_to_end"]:
                        ending_reason = f"mutual_agreement: {other_agent_decision['reasoning']}"
                        print(f"\n🤝 {current_speaker.name} agrees to end: {other_agent_decision['reasoning']}")
                        break
                    else:
                        print(f"\n↩️ {current_speaker.name} wants to continue: {other_agent_decision['reasoning']}")
                        # Continue conversation
            
            # Switch speakers for next turn
            current_speaker, current_listener = current_listener, current_speaker
            current_message = response
            
            # Natural conversation pacing
            await asyncio.sleep(0.5)
        
        else:
            print(f"\n⏰ Conversation reached safety limit ({self.max_turns} turns)")
        
        print(f"\n{'='*60}")
        print(f"🏁 Conversation ended: {ending_reason}")
        
        # Show relationship development and analysis
        await self._show_conversation_analysis()
    
    async def _get_intelligent_response(
        self, 
        agent: CharacterAgent, 
        message: str, 
        other_agent: CharacterAgent
    ) -> Dict[str, Any]:
        """Get response with intelligent ending decision"""
        
        # Build conversation context
        context_summary = self._build_conversation_context()
        
        # Create intelligent prompt for natural decision-making
        intelligent_prompt = f"""
You are {agent.name}. You're having a natural conversation with {other_agent.name}.

{context_summary}

Current message: "{message}"

Respond naturally as your character would. After your response, honestly assess whether this conversation feels like it should continue or naturally end.

Consider as your character would:
- Has this topic been adequately explored?
- Are you satisfied with the discussion?
- Do you have natural character reasons to end (other obligations, social cues, etc.)?
- Is the conversation reaching a natural conclusion?
- Are you starting to repeat yourself or feel the discussion is complete?

Format your response EXACTLY like this:

RESPONSE: [Your natural character response here]

ENDING_ASSESSMENT:
Want to end: [YES/NO]
Reasoning: [Explain why you do or don't want to end, staying in character]
Confidence: [1-10, how certain are you about this decision]

Be authentic to your character - don't force continuation or ending.
"""
        
        # Get response from agent
        full_response = await agent.process_message(intelligent_prompt, {
            "from_agent": other_agent.agent_id,
            "conversation_turn": self.turn_count,
            "conversation_history": self.conversation_history[-3:],
            "intelligent_ending_mode": True,
            "other_agent_name": other_agent.name
        })
        
        # Parse the structured response
        return self._parse_intelligent_response(full_response, agent.name)
    
    def _build_conversation_context(self, last_n_turns: int = 4) -> str:
        """Build context from recent conversation"""
        if not self.conversation_history:
            return "This is the beginning of your conversation."
        
        context_lines = [f"Conversation so far ({len(self.conversation_history)} exchanges):"]
        
        recent_exchanges = self.conversation_history[-last_n_turns:]
        for exchange in recent_exchanges:
            context_lines.append(f"{exchange['speaker']}: {exchange['message']}")
            context_lines.append(f"{exchange['listener']}: {exchange['response']}")
        
        # Add subtle context about conversation length
        total_exchanges = len(self.conversation_history)
        if total_exchanges >= 6:
            context_lines.append(f"\nNote: You've had {total_exchanges} substantial exchanges.")
        if total_exchanges >= 10:
            context_lines.append("This has been quite an extended discussion.")
        
        return "\n".join(context_lines)
    
    def _parse_intelligent_response(self, full_response: str, agent_name: str) -> Dict[str, Any]:
        """Parse the agent's structured response"""
        try:
            # Extract response part
            response_match = re.search(r'RESPONSE:\s*(.*?)(?=ENDING_ASSESSMENT:|$)', full_response, re.DOTALL)
            response = response_match.group(1).strip() if response_match else full_response
            
            # Extract ending assessment
            wants_to_end = False
            reasoning = "No clear reasoning provided"
            confidence = 5
            
            # Look for YES/NO
            end_match = re.search(r'Want to end:\s*(YES|NO)', full_response, re.IGNORECASE)
            if end_match:
                wants_to_end = end_match.group(1).upper() == "YES"
            
            # Extract reasoning
            reasoning_match = re.search(r'Reasoning:\s*(.*?)(?=Confidence:|$)', full_response, re.DOTALL)
            if reasoning_match:
                reasoning = reasoning_match.group(1).strip()
            
            # Extract confidence
            confidence_match = re.search(r'Confidence:\s*(\d+)', full_response)
            if confidence_match:
                confidence = int(confidence_match.group(1))
                confidence = max(1, min(10, confidence))  # Clamp to 1-10
            
            return {
                "response": response,
                "wants_to_end": wants_to_end,
                "reasoning": reasoning,
                "confidence": confidence,
                "agent_name": agent_name
            }
            
        except Exception as e:
            print(f"Warning: Could not parse response from {agent_name}: {e}")
            # Fallback to basic response
            return {
                "response": full_response,
                "wants_to_end": False,
                "reasoning": "Failed to parse ending assessment",
                "confidence": 5,
                "agent_name": agent_name
            }
    
    async def _get_ending_consensus(
        self, 
        other_agent: CharacterAgent, 
        previous_response: str, 
        ending_reasoning: str
    ) -> Dict[str, Any]:
        """Get the other agent's opinion on ending the conversation"""
        
        consensus_prompt = f"""
You are {other_agent.name}. The other person just said:
"{previous_response}"

They're suggesting the conversation might naturally end, reasoning: "{ending_reasoning}"

As your character, do you agree this conversation should end now, or do you want to continue?

Respond naturally, then add:

CONSENSUS:
Agree to end: [YES/NO]
Reasoning: [Your character's reasoning]

Be authentic to your character's personality and interests.
"""
        
        response = await other_agent.process_message(consensus_prompt, {
            "conversation_turn": self.turn_count,
            "consensus_check": True
        })
        
        # Parse consensus
        try:
            agree_match = re.search(r'Agree to end:\s*(YES|NO)', response, re.IGNORECASE)
            agrees = agree_match.group(1).upper() == "YES" if agree_match else False
            
            reasoning_match = re.search(r'Reasoning:\s*(.*?)$', response, re.DOTALL)
            reasoning = reasoning_match.group(1).strip() if reasoning_match else "No reasoning provided"
            
            return {
                "agrees_to_end": agrees,
                "reasoning": reasoning,
                "full_response": response
            }
            
        except Exception:
            return {
                "agrees_to_end": False,
                "reasoning": "Could not determine consensus",
                "full_response": response
            }
    
    async def _show_conversation_analysis(self):
        """Show detailed conversation analysis"""
        print(f"\n📊 Conversation Analysis:")
        print("-" * 50)
        
        # Basic metrics
        total_turns = len(self.conversation_history)
        avg_response_length = sum(len(ex['response']) for ex in self.conversation_history) / total_turns if total_turns > 0 else 0
        
        print(f"📈 Metrics:")
        print(f"  • Total exchanges: {total_turns}")
        print(f"  • Average response length: {avg_response_length:.1f} characters")
        
        # Ending analysis
        ending_attempts = sum(1 for ex in self.conversation_history if ex.get('wants_to_end', False))
        print(f"  • Natural ending signals: {ending_attempts}")
        
        if ending_attempts > 0:
            last_ending_attempt = None
            for ex in reversed(self.conversation_history):
                if ex.get('wants_to_end', False):
                    last_ending_attempt = ex
                    break
            
            if last_ending_attempt:
                print(f"  • Final ending confidence: {last_ending_attempt['confidence']}/10")
        
        # Show relationship development
        await self._show_relationship_development()
    
    async def _show_relationship_development(self):
        """Show how the agents' relationships have developed"""
        print(f"\n🤝 Relationship Development:")
        print("-" * 40)
        
        # Check agent1's view of agent2
        agent1_relationship = self.agent1.memory.relationships.get(self.agent2.agent_id, {})
        print(f"{self.agent1.name}'s view of {self.agent2.name}:")
        if agent1_relationship:
            for key, value in agent1_relationship.items():
                print(f"  • {key}: {value}")
        else:
            print(f"  • No specific relationship data recorded")
        
        print()
        
        # Check agent2's view of agent1
        agent2_relationship = self.agent2.memory.relationships.get(self.agent1.agent_id, {})
        print(f"{self.agent2.name}'s view of {self.agent1.name}:")
        if agent2_relationship:
            for key, value in agent2_relationship.items():
                print(f"  • {key}: {value}")
        else:
            print(f"  • No specific relationship data recorded")
    
    def get_conversation_summary(self) -> str:
        """Get a summary of the conversation"""
        if not self.conversation_history:
            return "No conversation has taken place."
        
        summary = f"Natural Conversation Summary ({len(self.conversation_history)} exchanges):\n"
        
        for exchange in self.conversation_history:
            summary += f"Turn {exchange['turn']}: {exchange['speaker']} → {exchange['listener']}"
            if exchange.get('wants_to_end'):
                summary += f" [wanted to end: {exchange['confidence']}/10]"
            summary += "\n"
        
        # Add ending analysis
        ending_attempts = [ex for ex in self.conversation_history if ex.get('wants_to_end')]
        if ending_attempts:
            summary += f"\nEnding signals: {len(ending_attempts)}"
            summary += f"\nFinal attempt confidence: {ending_attempts[-1]['confidence']}/10"
        
        return summary


async def create_agents_from_files(agent1_file: str, agent2_file: str) -> Tuple[CharacterAgent, CharacterAgent]:
    """Create two agents from character JSON files"""
    
    # Extract agent IDs from file paths (remove .json extension and path)
    agent1_id = Path(agent1_file).stem
    agent2_id = Path(agent2_file).stem
    
    print(f"🎭 Creating agent from {agent1_file}...")
    agent1 = CharacterAgent(
        agent_id=agent1_id,
        character_file=agent1_file
    )
    
    print(f"🎭 Creating agent from {agent2_file}...")
    agent2 = CharacterAgent(
        agent_id=agent2_id,
        character_file=agent2_file
    )
    
    print(f"\n✅ Both agents created successfully!")
    print(f"Agent 1: {agent1.name}")
    print(f"Agent 2: {agent2.name}")
    
    return agent1, agent2


async def demonstrate_character_driven_conversation(
    agent1_file: str = "characters/sherlock_holmes.json",
    agent2_file: str = "characters/dr_watson.json",
    topic: Optional[str] = None
):
    """Demonstrate a character-driven conversation between any two characters"""
    
    # Create agents from files
    agent1, agent2 = await create_agents_from_files(agent1_file, agent2_file)
    
    # Create character-driven conversation manager
    conversation = CharacterDrivenConversation(agent1, agent2)
    
    # Use provided topic or generate a generic one
    if topic is None:
        topic = f"Hello {agent2.name}, I wanted to discuss something important with you. What are your thoughts on our current situation?"
    
    await conversation.start_natural_conversation(topic)
    
    # Show conversation summary
    print(f"\n📊 {conversation.get_conversation_summary()}")


async def demonstrate_multiple_scenarios(
    agent1_file: str = "characters/sherlock_holmes.json",
    agent2_file: str = "characters/dr_watson.json"
):
    """Demonstrate different conversation scenarios with any two characters"""
    
    # Create agents once
    agent1, agent2 = await create_agents_from_files(agent1_file, agent2_file)
    
    # Generic scenarios that work with any characters
    scenarios = [
        {
            "title": "General Discussion",
            "topic": f"Hello {agent2.name}, I've been thinking about something interesting and wanted to get your perspective on it."
        },
        {
            "title": "Problem Solving", 
            "topic": f"{agent2.name}, I'm facing a challenging situation and could use your insight. What would you do in my position?"
        },
        {
            "title": "Knowledge Exchange",
            "topic": f"I've learned something fascinating recently, {agent2.name}. I think you'd find it quite intriguing."
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n\n🎬 Scenario {i}: {scenario['title']}")
        print("=" * 70)
        
        conversation = CharacterDrivenConversation(agent1, agent2)
        await conversation.start_natural_conversation(scenario["topic"])
        
        if i < len(scenarios):
            print("\n⏳ Brief pause before next scenario...")
            await asyncio.sleep(2)


async def run_custom_conversation(
    agent1_file: str,
    agent2_file: str, 
    topic: str,
    scenarios: Optional[List[Dict[str, str]]] = None
):
    """Run a conversation with custom characters, topic, and optional scenarios"""
    
    print(f"🎭 Custom Conversation Setup")
    print("=" * 50)
    print(f"Character 1: {agent1_file}")
    print(f"Character 2: {agent2_file}")
    print(f"Topic: {topic}")
    print("=" * 50)
    
    # Create agents
    agent1, agent2 = await create_agents_from_files(agent1_file, agent2_file)
    
    if scenarios:
        # Run multiple scenarios
        for i, scenario in enumerate(scenarios, 1):
            print(f"\n\n🎬 Scenario {i}: {scenario.get('title', f'Scenario {i}')}")
            print("=" * 70)
            
            conversation = CharacterDrivenConversation(agent1, agent2)
            await conversation.start_natural_conversation(scenario["topic"])
            
            if i < len(scenarios):
                print("\n⏳ Brief pause before next scenario...")
                await asyncio.sleep(2)
    else:
        # Single conversation
        conversation = CharacterDrivenConversation(agent1, agent2)
        await conversation.start_natural_conversation(topic)
        
        # Show conversation summary
        print(f"\n📊 {conversation.get_conversation_summary()}")


def get_available_characters(characters_dir: str = "characters") -> List[str]:
    """Get list of available character files"""
    characters_path = Path(characters_dir)
    if not characters_path.exists():
        return []
    
    return [str(f) for f in characters_path.glob("*.json")]


async def interactive_character_selection():
    """Interactive character selection for conversations"""
    
    print("🎭 Character Selection")
    print("=" * 30)
    
    # Get available characters
    available_chars = get_available_characters()
    
    if len(available_chars) < 2:
        print("❌ Need at least 2 character files in the 'characters' directory")
        return
    
    print("Available characters:")
    for i, char_file in enumerate(available_chars, 1):
        char_name = Path(char_file).stem.replace("_", " ").title()
        print(f"{i}. {char_name} ({char_file})")
    
    # For demo purposes, we'll use the first two available
    # In a real app, you could add input() for user selection
    agent1_file = available_chars[0]
    agent2_file = available_chars[1] if len(available_chars) > 1 else available_chars[0]
    
    print(f"\n🎯 Selected characters:")
    print(f"Character 1: {agent1_file}")
    print(f"Character 2: {agent2_file}")
    
    # Generic topic that works with any characters
    topic = "I wanted to start a conversation with you about something that's been on my mind lately. What do you think about the current state of things?"
    
    await demonstrate_character_driven_conversation(agent1_file, agent2_file, topic)


async def main():
    """Main function to run the demonstration"""
    print("🎭 Universal Character-Driven Conversation System")
    print("=" * 60)
    
    try:
        # Example usage scenarios
        print("Choose demonstration mode:")
        print("1. Default characters (if available)")
        print("2. Interactive character selection")
        print("3. Custom conversation example")
        print("4. Multiple scenarios with any characters")
        
        # For this demo, let's show different examples
        # In a real implementation, you could add input() here
        demo_mode = "3"  # Change this to test different modes
        
        if demo_mode == "1":
            # Try default characters, fallback to available ones
            try:
                await demonstrate_character_driven_conversation()
            except Exception as e:
                print(f"⚠️ Default characters not found: {e}")
                print("🔄 Falling back to available characters...")
                await interactive_character_selection()
        
        elif demo_mode == "2":
            await interactive_character_selection()
        
        elif demo_mode == "3":
            # Example with custom characters
            custom_scenarios = [
                {
                    "title": "First Meeting",
                    "topic": "What was your favorite moment in your career?"
                },
                {
                    "title": "Problem Discussion",
                    "topic": "I've been facing an interesting challenge lately and would appreciate your perspective on it."
                },
                {
                    "title": "Knowledge Sharing",
                    "topic": "I recently came across something fascinating that I think you might find intriguing."
                }
            ]
            
            # You can change these to any character files you have
            await run_custom_conversation(
                agent1_file="characters/michael_jordan.json",  # Change these paths
                agent2_file="characters/scottie_pippen.json",        # to your character files
                topic="I wanted to have a thoughtful discussion with you about something important.",
                scenarios=custom_scenarios[:1]  # Just run first scenario
            )
        
        elif demo_mode == "4":
            # Multiple scenarios with default or available characters
            try:
                await demonstrate_multiple_scenarios()
            except Exception as e:
                print(f"⚠️ Error with default characters: {e}")
                # Fallback to generic demonstration
                available_chars = get_available_characters()
                if len(available_chars) >= 2:
                    await demonstrate_multiple_scenarios(available_chars[0], available_chars[1])
                else:
                    print("❌ Need at least 2 character files to run demonstration")
        
        print("\n✅ Character-driven conversation demonstration completed!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


# Example usage functions for different scenarios
async def example_business_meeting():
    """Example: Business characters having a meeting"""
    await run_custom_conversation(
        agent1_file="characters/ceo.json",
        agent2_file="characters/cto.json", 
        topic="I wanted to discuss our Q4 strategy and get your thoughts on the technical implementation."
    )


async def example_academic_discussion():
    """Example: Academic characters discussing research"""
    await run_custom_conversation(
        agent1_file="characters/professor_smith.json",
        agent2_file="characters/dr_jones.json",
        topic="I've been reviewing your latest research paper and have some fascinating insights to share."
    )


async def example_creative_collaboration():
    """Example: Creative characters collaborating"""
    await run_custom_conversation(
        agent1_file="characters/artist.json", 
        agent2_file="characters/writer.json",
        topic="I have an idea for a creative project that could combine our different artistic perspectives."
    )


async def example_historical_figures():
    """Example: Historical figures meeting"""
    scenarios = [
        {
            "title": "Philosophical Exchange",
            "topic": "I've been contemplating the nature of knowledge and reality. What are your thoughts on this fundamental question?"
        },
        {
            "title": "Scientific Discussion", 
            "topic": "I've made some observations that challenge conventional thinking. I'm curious about your perspective."
        }
    ]
    
    await run_custom_conversation(
        agent1_file="characters/einstein.json",
        agent2_file="characters/newton.json",
        topic="It's fascinating to meet another scientist. I'd love to discuss our different approaches to understanding the universe.",
        scenarios=scenarios
    )


if __name__ == "__main__":
    asyncio.run(main())