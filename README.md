
# AI Choice-Based Game

This project integrates OpenAI's GPT-3.5 model to create a choice-based game. The AI generates dynamic responses based on user inputs, allowing for immersive, choice-driven gameplay.

## Project Structure

- `backend/`: Contains the Flask backend and OpenAI integration.
  - `openai_integration.py`: Script responsible for interacting with OpenAI's GPT-3.5 API to generate responses.
- `frontend/`: React-based frontend for user interaction.
- `.venv/`: Python virtual environment containing dependencies.

## Requirements

Before running the project, ensure you have the following installed:

- Python 3.11+
- Node.js (for the frontend)
- OpenAI API Key

## Setup

### Backend

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd ai_choice_game
   ```

2. Set up the virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install backend dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the root directory and add your OpenAI API key:
   ```bash
   OPENAI_API_KEY=<your-api-key>
   ```

### Frontend

1. Navigate to the `frontend/` directory:
   ```bash
   cd frontend
   ```

2. Install the required Node modules:
   ```bash
   npm install
   ```

### Running the Project

#### Backend

To start the Flask backend:
```bash
cd backend
python openai_integration.py
```

#### Frontend

To start the React frontend:
```bash
cd frontend
npm start
```

The backend will handle API requests, while the frontend will provide the user interface for interaction.

## Usage

Once both the backend and frontend are running, navigate to `http://localhost:3000` in your browser to interact with the choice-based game. You can input your choices and receive AI-generated responses from the GPT-3.5 model.

## Sample Test

You can run a test prompt in the `openai_integration.py` file to ensure that the API is working correctly:

```bash
python openai_integration.py
```

This will send a prompt ("Describe a mysterious forest with two paths") to the OpenAI API and print the response in the console.

## Issues and Contributions

If you encounter any issues or would like to contribute to this project, please feel free to open an issue or submit a pull request.


