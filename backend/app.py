from flask import Flask, jsonify, request
from openai_integration import get_gpt35_response
import json
import re

app = Flask(__name__)

# Global variable to store story context for simplicity (you may want to improve this with session management)
story_context = ""

# Function to extract valid JSON from the response
def extract_json_from_response(response):
    try:
        # Match the JSON structure inside the response
        json_match = re.search(r"\{.*?\}", response, re.DOTALL)
        if json_match:
            json_content = json_match.group(0)
            return json.loads(json_content)  # Convert the string to JSON
        else:
            return None  # Return None if no JSON structure is found
    except json.JSONDecodeError:
        return None  # Handle JSON decode errors gracefully

# Route to start the game (resets story context)
@app.route('/start', methods=['GET'])
def start_game():
    global story_context
    story_context = ""  # Reset the story context when starting a new game

    prompt = """
    You are telling a short, interactive story. The player is standing at a crossroads. 
    Continue the story in **plain language only**, without any code, instructions, or examples. 
    Write exactly 3 sentences that describe what happens next. 
    After the story, provide exactly 2 choices for the player, labeled '1' and '2'. 
    Format the response in this exact JSON structure:
    {
      'story': 'story text here',
      'choices': ['choice 1', 'choice 2']
    }
    Do not include any programming code, technical instructions, or comments. Only return the plain JSON.
    """
    response = get_gpt35_response(prompt)
    story_data = extract_json_from_response(response)

    if story_data and "story" in story_data and "choices" in story_data:
        story_context = story_data['story']  # Initialize the story context
        return jsonify(story_data)
    else:
        return jsonify({
            "story": "There was an issue generating the initial story. Please try again.",
            "choices": ["1. Retry", "2. Exit"]
        })

# Route to handle player choice
@app.route('/choice', methods=['POST'])
def player_choice():
    global story_context
    data = request.get_json()
    choice = data.get('choice')

    if choice not in [1, 2]:
        return jsonify({"error": "Invalid choice"}), 400

    # Add the player's choice to the existing story context
    choice_text = f"The player chose option {choice}."

    # Build the prompt to continue the story
    prompt = f"""
    The story so far: "{story_context}"
    Based on the player's decision, continue the story in **plain language only**, without any code, instructions, or examples.

    Write exactly 3 sentences that describe what happens next in the story. 
    After the story, provide exactly 2 new choices for the player in this JSON structure:
    {{
    "story": "story text here",
    "choices": ["choice 1", "choice 2"]
    }}

    Do not include any code, comments, or the phrase 'the player chose option X'. Only return the JSON.
    """


    # Get response from GPT-3.5 Turbo
    response = get_gpt35_response(prompt)
    story_data = extract_json_from_response(response)

    if story_data and "story" in story_data and "choices" in story_data:
        # Append the new part of the story to the existing context
        story_context += " " + story_data['story']
        return jsonify(story_data)
    else:
        return jsonify({
            "story": "There was an issue generating the next part of the story. Please try again.",
            "choices": ["1. Retry", "2. Exit"]
        })

if __name__ == '__main__':
    app.run(debug=True)
