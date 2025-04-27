# AI Choice-Based Game with LangGraph

This project creates an interactive choice-based adventure game using LangGraph and DeepSeek's AI model. The game generates dynamic responses based on user inputs, allowing for immersive, choice-driven gameplay.

## Project Structure

- **backend/**: Contains the Flask backend and AI integration.
  - **app.py**: Flask application that handles HTTP requests.
  - **game_graph.py**: LangGraph implementation for managing game state and AI interactions.
- **frontend/**: React-based frontend for user interaction.
- **.venv/**: Python virtual environment containing dependencies.

## Requirements

Before running the project, ensure you have the following installed:

- Python 3.11+
- Node.js (for the frontend)
- DeepSeek API Key

## Setup

### Backend

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd ai_choice_game
   ```

2. Set up the virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
   ```

3. Install backend dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the root directory and add your DeepSeek API key:
   ```
   DEEPSEEK_API_KEY=<your-api-key>
   ```

### Frontend

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install the required Node modules:
   ```bash
   npm install
   ```

## Running the Project

### Backend

To start the Flask backend:
```bash
flask run
```

### Frontend

To start the React frontend:
```bash
npm start
```

The backend will handle API requests and manage game state using LangGraph, while the frontend will provide the user interface for interaction.

## Architecture

### LangGraph Implementation

The project uses LangGraph to create a stateful, directed graph for managing the game flow:

- **States**: Tracks story context, current story segment, available choices, and message history.
- **Nodes**: Represents operations like generating stories and handling player choices.
- **Edges**: Defines transitions between states based on player actions.

### DeepSeek Integration

The game uses DeepSeek's AI model to generate creative and contextually appropriate story segments and choices. The API integration:

- Maintains conversation context across multiple turns
- Ensures proper formatting of responses as JSON
- Handles errors gracefully

## API Endpoints

- **GET /start**: Initializes a new game and returns the initial story and choices.
- **POST /choice**: Accepts a player's choice and returns the next part of the story with new choices.
- **POST /end**: Ends the current game session.

## User Interface

The frontend provides a minimalist black and white interface with:

- A central dialogue box displaying the current story
- Four choice buttons for player decisions
- Status messages for error handling and game state

## Development

### Dependencies

#### Backend:

- Flask
- LangGraph
- python-dotenv
- requests

#### Frontend:

- React
- Axios for API calls
- CSS for styling

## Issues and Contributions

If you encounter any issues or would like to contribute to this project, please feel free to open an issue or submit a pull request.