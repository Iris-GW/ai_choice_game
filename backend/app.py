from flask import Flask, jsonify, request
from game_graph import start_new_game, make_choice, end_game
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

@app.route('/start', methods=['GET'])
def start_game():
    """Start a new game."""
    try:
        game_state = start_new_game()
        return jsonify(game_state)
    except Exception as e:
        return jsonify({
            "story": f"Error starting game: {str(e)}",
            "choices": ["1. Retry", "2. Exit", "3. Start a new story", "4. Try a different theme"]
        })

@app.route('/choice', methods=['POST'])
def player_choice():
    """Handle a player's choice."""
    try:
        data = request.get_json()
        choice = data.get('choice')
        
        if choice not in [1, 2, 3, 4]:
            return jsonify({"error": "Invalid choice"}), 400
            
        game_state = make_choice(choice)
        return jsonify(game_state)
    except Exception as e:
        return jsonify({
            "story": f"Error processing choice: {str(e)}",
            "choices": ["1. Retry", "2. Go back", "3. Try a different path", "4. Exit game"]
        })

@app.route('/end', methods=['POST'])
def end_current_game():
    """End the current game."""
    try:
        result = end_game()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"Error ending game: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
