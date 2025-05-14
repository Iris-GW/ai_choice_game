import asyncio
import json
import re
import os
from typing import Dict, List, Optional
from quart import Quart, jsonify, request
from dotenv import load_dotenv
import aiohttp
from quart_cors import cors

# Load environment variables
load_dotenv()

# Get API key from environment variables
api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    raise ValueError("DEEPSEEK_API_KEY environment variable is not set")

# Create Quart app (async version of Flask)
app = Quart(__name__)
app = cors(app, allow_origin="*")  # For development only

# Session storage - maps session_id to game state
sessions = {}

# ------------------------
# DeepSeek API Integration
# ------------------------

async def generate_ai_response(messages: List[Dict[str, str]]) -> str:
    """Send a request to DeepSeek API and get a response asynchronously"""
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "deepseek-chat",
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 250
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    error_text = await response.text()
                    print(f"API Error {response.status}: {error_text}")
                    return None
        except Exception as e:
            print(f"Request error: {str(e)}")
            return None

# -----------------------
# Game State Management
# -----------------------

def extract_json(text: str) -> Optional[Dict]:
    """Extract JSON from the AI response text with improved pattern matching"""
    if not text:
        print("Empty response received")
        return None
        
    try:
        # Print the response for debugging
        print(f"AI Response: {text[:200]}...")  # Print first 200 chars for debugging
        
        # Try different regex patterns to find JSON
        # Pattern 1: Look for the most complete JSON object
        json_match = re.search(r'\{(?:[^{}]|(?:\{[^{}]*\}))*\}', text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0).replace("'", "\"")
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                print(f"Failed to parse JSON using pattern 1: {json_str[:100]}...")
        
        # Pattern 2: More aggressive approach - find anything between curly braces
        json_match = re.search(r'\{.*?\}', text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0).replace("'", "\"")
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                print(f"Failed to parse JSON using pattern 2: {json_str[:100]}...")
        
        # Pattern 3: Last resort - try to extract structured fields manually
        story_match = re.search(r'"story"\s*:\s*"([^"]*)"', text)
        choices_match = re.search(r'"choices"\s*:\s*\[(.*?)\]', text)
        
        if story_match and choices_match:
            story = story_match.group(1)
            choices_text = choices_match.group(1)
            choices = re.findall(r'"([^"]*)"', choices_text)
            
            return {
                "story": story,
                "choices": choices
            }
            
        print("No valid JSON pattern found in response")
        return None
    except Exception as e:
        print(f"Error extracting JSON: {str(e)}")
        return None

async def create_new_game() -> Dict:
    """Create a new game session and return the initial story"""
    # System prompt for consistent JSON formatting
    system_prompt = """You are creating an interactive story game with moral choices.
IMPORTANT: Always respond with valid JSON in EXACTLY this format, with no additional text before or after:
{
  "story": "The story text goes here",
  "choices": ["Virtuous choice", "Good choice", "Selfish choice", "Evil choice"]
}
The choices should represent a moral spectrum from good to evil.
Use escaped quotes (\") within the text if needed. Do not include backticks, code blocks, or any other formatting.
Your responses should be creative and engaging."""

    # Initial prompt to start the story
    user_prompt = """Create the beginning of an interactive story with moral choices. 
The player is standing at a crossroads, both literal and metaphorical.
Write exactly 3 sentences that describe what happens next.
After the story, provide exactly 4 choices for the player, arranged from most virtuous/moral to most selfish/evil."""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    # Get response from AI
    response = await generate_ai_response(messages)
    if not response:
        return {
            "story": "There was an error connecting to the AI service. Please try again.",
            "choices": ["Make the virtuous choice", "Make a good choice", 
                        "Make a selfish choice", "Make a dark choice"]
        }
    
    # Extract JSON data
    story_data = extract_json(response)
    if not story_data or "story" not in story_data or "choices" not in story_data:
        return {
            "story": "There was an issue generating the story. Please try again.",
            "choices": ["Retry", "Exit", "Start a new story", "Try a different theme"]
        }
    
    # Create a new session
    session_id = f"game_{len(sessions) + 1}_{os.urandom(4).hex()}"
    
    # Store session data
    sessions[session_id] = {
        "story_context": story_data["story"],
        "messages": messages + [{"role": "assistant", "content": response}],
        "moral_score": 0  # 0 = neutral starting point
    }
    
    # Return response with session ID
    return {
        "session_id": session_id,
        "story": story_data["story"],
        "choices": story_data["choices"]
    }

async def process_player_choice(session_id: str, choice: int) -> Dict:
    """Process a player's choice and continue the story"""
    # Check if session exists
    if session_id not in sessions:
        return {
            "error": "Invalid or expired session"
        }
    
    session = sessions[session_id]
    
    # Get the last AI response
    if not session["messages"] or len(session["messages"]) < 1:
        return {
            "error": "Invalid session state - no message history"
        }
        
    last_response = session["messages"][-1]["content"]
    story_data = extract_json(last_response)
    
    # Handle case where we can't parse the previous response
    if not story_data or "choices" not in story_data:
        print(f"Failed to parse previous AI response for session {session_id}")
        # Use fallback choices
        choices = ["Continue virtuously", "Take a good path", "Choose selfishly", "Embrace darkness"]
        chosen_option = choices[min(choice-1, len(choices)-1)]
    else:
        # Validate choice against available options
        if choice < 1 or choice > len(story_data["choices"]):
            return {
                "error": f"Invalid choice number {choice}. Valid range: 1-{len(story_data['choices'])}"
            }
        chosen_option = story_data["choices"][choice-1]
    
    # Determine the moral nature of the choice (1=most good, 4=most evil)
    moral_alignment = choice
    moral_descriptor = ["virtuous", "good", "selfish", "dark"][min(moral_alignment-1, 3)]
    
    # Update moral score
    moral_change = {1: 2, 2: 1, 3: -1, 4: -2}[min(choice, 4)]
    session["moral_score"] += moral_change
    
    # Create prompt for the next part of the story
    prompt = f"""The story so far: "{session["story_context"]}"

The player chose: "{chosen_option}" (a {moral_descriptor} choice)

Continue the story based on this choice. The consequences should subtly reflect the moral nature of their decision.
Write exactly 3 sentences that describe what happens next.
After the story, provide exactly 4 new choices for the player, arranged from most virtuous/moral to most selfish/evil.
Remember to structure your response as valid JSON with "story" and "choices" fields."""

    # Add player choice to messages
    session["messages"].append({"role": "user", "content": prompt})
    
    # Get response from AI
    response = await generate_ai_response(session["messages"])
    if not response:
        return {
            "error": "Failed to generate response from AI service"
        }
    
    # Print full response for debugging
    print(f"Full AI response: {response}")
    
    # Extract JSON data
    new_story_data = extract_json(response)
    if not new_story_data or "story" not in new_story_data or "choices" not in new_story_data:
        # Try to generate a recovery response
        return {
            "error": "Failed to parse AI response",
            "story": "There was an issue generating the next part of the story. The AI's response couldn't be parsed correctly.",
            "choices": ["Try again", "Go back", "Start over", "End game"]
        }
    
    # Update session
    session["messages"].append({"role": "assistant", "content": response})
    session["story_context"] += " " + new_story_data["story"]
    
    # Return response with session ID
    return {
        "session_id": session_id,
        "story": new_story_data["story"],
        "choices": new_story_data["choices"],
        "moral_alignment": "good" if session["moral_score"] > 3 else 
                           "mostly_good" if session["moral_score"] > 0 else
                           "neutral" if session["moral_score"] == 0 else
                           "mostly_evil" if session["moral_score"] > -3 else
                           "evil"
    }

# --------------------
# API Routes
# --------------------

@app.route('/start', methods=['GET'])
async def start_game():
    """Start a new game and return the initial story"""
    try:
        result = await create_new_game()
        return jsonify(result)
    except Exception as e:
        print(f"Error starting game: {str(e)}")
        return jsonify({
            "error": f"Error starting game: {str(e)}"
        }), 500

@app.route('/choice', methods=['POST'])
async def make_choice():
    """Process a player's choice and continue the story"""
    try:
        data = await request.get_json()
        
        # Validate request
        if not data or "choice" not in data or "session_id" not in data:
            return jsonify({"error": "Missing choice or session_id"}), 400
        
        choice = data["choice"]
        session_id = data["session_id"]
        
        # Process choice
        result = await process_player_choice(session_id, choice)
        
        if "error" in result:
            return jsonify(result), 400
            
        return jsonify(result)
    except Exception as e:
        print(f"Error processing choice: {str(e)}")
        return jsonify({
            "error": f"Error processing choice: {str(e)}"
        }), 500

@app.route('/end', methods=['POST'])
async def end_game():
    """End a game session"""
    try:
        data = await request.get_json()
        
        # Validate request
        if not data or "session_id" not in data:
            return jsonify({"error": "Missing session_id"}), 400
        
        session_id = data["session_id"]
        
        # Check if session exists
        if session_id not in sessions:
            return jsonify({"error": "Invalid or expired session"}), 400
        
        # Remove session
        del sessions[session_id]
        
        return jsonify({"message": "Game ended successfully"})
    except Exception as e:
        print(f"Error ending game: {str(e)}")
        return jsonify({
            "error": f"Error ending game: {str(e)}"
        }), 500

@app.route('/summarize', methods=['POST'])
async def summarize_story():
    """Generate a brief summary of the story and player choice"""
    try:
        data = await request.get_json()
        
        # Validate request
        if not data or "story" not in data:
            return jsonify({"error": "Missing story content"}), 400
        
        story = data["story"]
        choice = data.get("choice", "")  # Get the player's choice if provided
        
        # Create prompt for summarization - different based on whether we have a choice
        system_prompt = """You are a storytelling assistant that creates concise narrative summaries.
Always respond with a JSON object containing only a single 'summary' field with your summary text.
Keep summaries poetic and under 100 characters while capturing both events and decisions."""

        # Modify prompt based on whether choice is available
        if choice:
            user_prompt = f"""Summarize this story excerpt AND the player's choice as a single narrative:
            
Story: {story}
Player chose: {choice}

Create a cohesive dramatic summary that weaves together what happened and what choice was made.
Be poetic but concise - like a line from a novel that captures both the event and decision."""
        else:
            user_prompt = f"""Summarize this story excerpt in one short sentence, capturing its essence:
            
{story}

Be poetic but concise."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # Get summary from AI
        response = await generate_ai_response(messages)
        if not response:
            # Default fallback based on whether we have a choice
            if choice:
                return jsonify({"summary": f"You chose {choice} as the world unfolded around you..."}), 200
            else:
                return jsonify({"summary": "Chapter in your ongoing adventure..."}), 200
            
        # Try to extract JSON
        summary_data = extract_json(response)
        if summary_data and "summary" in summary_data:
            return jsonify({"summary": summary_data["summary"]}), 200
        
        # If can't parse JSON, extract text directly
        summary_match = re.search(r'"summary"\s*:\s*"([^"]*)"', response)
        if summary_match:
            return jsonify({"summary": summary_match.group(1)}), 200
            
        # Fallback - use response text directly with cleanup
        clean_response = re.sub(r'[\{\}\"\[\]]', '', response)  # Remove JSON syntax
        clean_response = re.sub(r'summary\s*:', '', clean_response).strip()  # Remove field name
        return jsonify({"summary": clean_response[:100] + "..." if len(clean_response) > 100 else clean_response}), 200
            
    except Exception as e:
        print(f"Error generating summary: {str(e)}")
        # Fallback with choice if available
        if "choice" in data and data["choice"]:
            return jsonify({"summary": f"You chose {data['choice']} and continued your journey..."}), 200
        else:
            return jsonify({"summary": "Chapter in your ongoing adventure..."}), 200

@app.route('/moral_choice', methods=['POST'])
async def generate_moral_choices():
    """Generate a set of choices ranging from good to evil for the current situation"""
    try:
        data = await request.get_json()
        
        # Validate request
        if not data or "story_context" not in data:
            return jsonify({"error": "Missing story context"}), 400
        
        story_context = data["story_context"]
        current_situation = data.get("current_situation", "")
        
        # Create prompt for generating moral choices
        system_prompt = """You are a storytelling assistant that creates morally diverse choices.
Always respond with a JSON object containing a 'choices' array with exactly 4 choices.
Structure the choices in a spectrum from most virtuous/good (first) to most selfish/evil (last).
Each choice should be morally distinct but realistic for the character and situation."""

        user_prompt = f"""Given the story context and current situation, generate 4 choices across a moral spectrum:

Story so far: {story_context}
Current situation: {current_situation}

Create 4 choices where:
1. First choice is clearly good/virtuous/selfless
2. Second choice is moderately good/positive
3. Third choice is morally ambiguous/selfish
4. Fourth choice is clearly evil/malicious/harmful

Ensure all choices make sense in context and represent realistic options a character might consider.
Avoid obvious tropes or cartoonish evil. Make choices subtle and interesting."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # Get response from AI
        response = await generate_ai_response(messages)
        if not response:
            return jsonify({
                "choices": [
                    "Do the selfless thing and help others",
                    "Take a balanced approach that's mostly good",
                    "Look out for your own interests first",
                    "Take advantage of the situation for your gain"
                ]
            }), 200
            
        # Extract JSON data
        choices_data = extract_json(response)
        if choices_data and "choices" in choices_data and len(choices_data["choices"]) == 4:
            return jsonify({"choices": choices_data["choices"]}), 200
            
        # Fallback if extraction fails
        return jsonify({
            "choices": [
                "Do the selfless thing and help others",
                "Take a balanced approach that's mostly good",
                "Look out for your own interests first",
                "Take advantage of the situation for your gain"
            ]
        }), 200
            
    except Exception as e:
        print(f"Error generating moral choices: {str(e)}")
        return jsonify({
            "error": f"Error generating moral choices: {str(e)}"
        }), 500

# --------------------
# Run the application
# --------------------

if __name__ == "__main__":
    app.run(debug=True, port=5001)