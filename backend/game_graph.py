from typing import Dict, List, TypedDict, Union, Optional
import os
import json
import re
import requests
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get DeepSeek API key
deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
if not deepseek_api_key:
    raise ValueError("DEEPSEEK_API_KEY environment variable is not set")

# Define our state
class GameState(TypedDict):
    story_context: str
    current_story: str
    choices: List[str]
    player_choice: Optional[int]
    messages: List[Union[HumanMessage, AIMessage, SystemMessage]]
    error: Optional[str]

# System prompt that ensures proper JSON formatting
SYSTEM_PROMPT = """You are an AI assistant creating an interactive story game.
Always respond with valid JSON in this exact format:
{
  "story": "The story text goes here",
  "choices": ["Choice 1", "Choice 2", "Choice 3", "Choice 4"]
}
Your responses should be creative, engaging and provide the player with 4 distinct choices.
"""

# Direct DeepSeek API integration
class DeepSeekAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.deepseek.com/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def invoke(self, messages):
        # Convert LangChain message objects to DeepSeek format
        formatted_messages = []
        for message in messages:
            if isinstance(message, SystemMessage):
                formatted_messages.append({"role": "system", "content": message.content})
            elif isinstance(message, HumanMessage):
                formatted_messages.append({"role": "user", "content": message.content})
            elif isinstance(message, AIMessage):
                formatted_messages.append({"role": "assistant", "content": message.content})
        
        # Prepare request payload
        payload = {
            "model": "deepseek-chat",
            "messages": formatted_messages,
            "temperature": 0.7,
            "max_tokens": 250
        }
        
        # Send request to DeepSeek API
        response = requests.post(self.base_url, headers=self.headers, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            # Return an AIMessage to maintain compatibility
            return AIMessage(content=content)
        else:
            # If there's an error, include the error details in the message
            error_msg = f"Error {response.status_code}: {response.text}"
            print(error_msg)
            return AIMessage(content=error_msg)

# Initialize the DeepSeek API client
model = DeepSeekAPI(api_key=deepseek_api_key)

# Initialize the story with a starting prompt
def initialize_game() -> GameState:
    """Initialize a new game state."""
    prompt = """
    Create the beginning of an interactive story. The player is standing at a crossroads.
    Write exactly 3 sentences that describe what happens next.
    After the story, provide exactly 4 choices for the player.
    """
    
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=prompt)
    ]
    
    return {
        "story_context": "",
        "current_story": "",
        "choices": [],
        "player_choice": None,
        "messages": messages,
        "error": None
    }

# Extract valid JSON from the AI response
def extract_json_from_response(response: str) -> Dict:
    """Extract valid JSON from the AI response."""
    try:
        # Match the JSON structure inside the response
        json_match = re.search(r"\{.*?\}", response, re.DOTALL)
        if json_match:
            json_content = json_match.group(0).replace("'", '"')  # Replace single quotes with double quotes
            return json.loads(json_content)
        else:
            return {"error": "No valid JSON found in response"}
    except json.JSONDecodeError as e:
        return {"error": f"JSON decode error: {str(e)}"}

# Generate story and choices
def generate_story(state: GameState) -> GameState:
    """Generate the next part of the story based on the current state."""
    try:
        # Get AI response
        ai_response = model.invoke(state["messages"])
        
        # Extract JSON from response
        story_data = extract_json_from_response(ai_response.content)
        
        if "error" in story_data:
            state["error"] = story_data["error"]
            state["current_story"] = "There was an issue generating the story. Please try again."
            state["choices"] = ["Retry", "Start Over", "Try a different path", "Exit"]
            return state
        
        # Update state with new story data
        state["current_story"] = story_data.get("story", "")
        state["choices"] = story_data.get("choices", [])
        
        # Update story context
        if state["story_context"]:
            state["story_context"] += " " + state["current_story"]
        else:
            state["story_context"] = state["current_story"]
            
        # Add AI response to message history
        state["messages"].append(ai_response)
        
        return state
    except Exception as e:
        state["error"] = f"Error generating story: {str(e)}"
        state["current_story"] = "There was an unexpected error. Please try again."
        state["choices"] = ["Retry", "Start Over", "Try a different path", "Exit"]
        return state

# Handle player choice
def handle_choice(state: GameState) -> GameState:
    """Process the player's choice and prepare for the next story segment."""
    choice = state.get("player_choice")
    
    if choice is None or choice < 1 or choice > 4:
        state["error"] = "Invalid choice"
        return state
    
    # Create a new prompt based on the player's choice
    choice_prompt = f"""
    The story so far: "{state['story_context']}"
    
    The player chose: "{state['choices'][choice-1]}"
    
    Continue the story based on this choice. Write exactly 3 sentences that describe what happens next.
    After the story, provide exactly 4 new choices for the player.
    """
    
    # Add the new prompt to messages
    state["messages"].append(HumanMessage(content=choice_prompt))
    
    # Reset player choice
    state["player_choice"] = None
    
    return state

# Determine if we should end the graph
def should_end(state: GameState) -> str:
    """Determine if the game should end based on the player's choice."""
    if state.get("player_choice") == -1:  # Special value to end the game
        return "end"
    return "continue"

# Create the game graph
def create_game_graph():
    """Create the game graph using LangGraph."""
    # Create a new graph
    workflow = StateGraph(GameState)
    
    # Add nodes for game flow
    workflow.add_node("generate_story", generate_story)
    workflow.add_node("handle_choice", handle_choice)
    
    # Set the entry point
    workflow.set_entry_point("generate_story")
    
    # Add edges
    workflow.add_edge("generate_story", "handle_choice")
    workflow.add_edge("handle_choice", "generate_story")
    
    # Add conditional edges for ending the game
    workflow.add_conditional_edges(
        "handle_choice",
        should_end,
        {
            "continue": "generate_story",
            "end": END
        }
    )
    
    # Compile the graph
    return workflow.compile()

# Initialize the game graph
graph = create_game_graph()

# Create a dictionary to store game states
game_states = {}

# Game session ID for persistent state
current_session_id = "game_session"

# Functions to interface with the game
def start_new_game():
    """Start a new game and return the initial state."""
    global current_session_id
    
    # Create a new session ID
    current_session_id = f"game_session_{os.urandom(4).hex()}"
    
    # Initialize game state
    state = initialize_game()
    
    # Generate initial story
    result = generate_story(state)
    
    # Store state in our dictionary
    game_states[current_session_id] = result
    
    return {
        "story": result["current_story"],
        "choices": result["choices"]
    }

def make_choice(choice: int):
    """Make a choice in the game and return the next state."""
    global current_session_id
    
    # Get current state from our dictionary
    state = game_states.get(current_session_id, initialize_game())
    
    # Set player choice
    state["player_choice"] = choice
    
    # Process the choice
    state = handle_choice(state)
    
    # Generate next story
    state = generate_story(state)
    
    # Store updated state
    game_states[current_session_id] = state
    
    return {
        "story": state["current_story"],
        "choices": state["choices"]
    }

def end_game():
    """End the current game."""
    global current_session_id
    
    # Clean up the game state
    if current_session_id in game_states:
        del game_states[current_session_id]
    
    return {"message": "Game ended"}