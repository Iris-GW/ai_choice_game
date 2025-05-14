# AI Choice-Based Game with Asyncio

This project creates an interactive choice-based adventure game using asynchronous Python and DeepSeek's AI model. The game generates dynamic responses based on user inputs, allowing for immersive, choice-driven gameplay with a morality system.

## Project Structure

- **backend/**: Contains the Quart backend and AI integration.
  - **app_async.py**: Quart application that handles HTTP requests asynchronously.
  - **deepseek_async_integration.py**: Asynchronous client for DeepSeek API.
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
   pip install quart quart-cors aiohttp python-dotenv
   ```

4. Create a .env file in the root directory and add your DeepSeek API key:
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

To start the Quart backend:
```bash
python backend/app_async.py
```

### Frontend

To start the React frontend:
```bash
cd frontend
npm start
```

The backend will handle API requests asynchronously, while the frontend will provide the user interface for interaction.

## Architecture

### Asynchronous Implementation

The project uses Python's asyncio to create a highly responsive, non-blocking game server:

- **Session Management**: Tracks game state across multiple interactions
- **Asynchronous API Calls**: Non-blocking calls to the DeepSeek API
- **Concurrent Request Handling**: Efficiently manages multiple simultaneous users

### Morality System

The game implements a morality spectrum that affects the story:

- Choices range from virtuous/good to selfish/evil
- Player decisions influence their character's moral alignment
- Story consequences reflect the ethical nature of choices made

### DeepSeek Integration

The game uses DeepSeek's AI model to generate creative and contextually appropriate story segments and choices. The API integration:

- Maintains conversation context across multiple turns
- Ensures proper formatting of responses as JSON
- Handles errors gracefully with fallback options

## API Endpoints

- **GET /start**: Initializes a new game and returns the initial story and choices.
- **POST /choice**: Accepts a player's choice and returns the next part of the story with new choices.
- **POST /end**: Ends the current game session.
- **POST /summarize**: Generates a summary of a story chapter and the player's choice.
- **POST /moral_choice**: Generates a set of choices ranging from good to evil based on the current situation.

## User Interface

The frontend provides an immersive interface with:

- A central dialogue box displaying the current story
- Four choice buttons for player decisions, color-coded by moral alignment
- A sidebar showing the player's journey with chapter summaries
- A moral alignment indicator showing the character's ethical path
- Status messages for error handling and game state

## Development

### Dependencies

#### Backend:

- Quart (async Flask alternative)
- Quart-CORS for cross-origin resource sharing
- aiohttp for async HTTP requests
- python-dotenv for environment variable management

#### Frontend:

- React for UI components
- CSS for styling
- Fetch API for async requests

## Performance

The asynchronous implementation offers several advantages over traditional approaches:

- Significantly reduced response times under load
- Better handling of concurrent users
- More efficient use of server resources
- Improved scalability for larger deployments

## Issues and Contributions

If you encounter any issues or would like to contribute to this project, please feel free to open an issue or submit a pull request.

## Future Enhancements

- Player character customization
- Persistent user accounts and saved games
- More complex branching narratives based on past choices
- Audio narration and sound effects
- Illustrations generated based on story content