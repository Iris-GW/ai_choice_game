import React, { useState, useEffect } from 'react';
import './App.css';

// API base URL - change this to your backend server URL
const API_BASE_URL = 'http://localhost:5001';

function App() {
    const [story, setStory] = useState("");
    const [choices, setChoices] = useState([]);
    const [statusMessage, setStatusMessage] = useState("Waiting for the story to load..."); 
    const [sessionId, setSessionId] = useState(null);
    const [loading, setLoading] = useState(false);
    const [gameHistory, setGameHistory] = useState([]); // To keep track of story progress
    const [choicesMade, setChoicesMade] = useState([]); // To track the choices player made
    const [chapterSummaries, setChapterSummaries] = useState([]); // To store AI-generated summaries
    const [moralAlignment, setMoralAlignment] = useState("neutral"); // To track moral alignment

    // Helper function to create summary from story
    const createSummary = (text) => {
        // If text is short enough, return it as is
        if (text.length <= 120) return text;
        
        // Otherwise, truncate and add ellipsis
        return text.substring(0, 117) + '...';
    };

    // Function to get AI-generated summary of a chapter and player's choice
    const getSummaryForChapter = async (storyText, playerChoice) => {
        try {
            const response = await fetch(`${API_BASE_URL}/summarize`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    story: storyText,
                    choice: playerChoice
                })
            });
            
            if (!response.ok) {
                throw new Error('Failed to generate chapter summary');
            }
            
            const data = await response.json();
            return data.summary;
        } catch (error) {
            console.error('Error getting chapter summary:', error);
            return `You chose "${playerChoice}" and continued your journey...`;
        }
    };

    // Fetch the initial story when the component mounts
    useEffect(() => {
        setLoading(true);
        console.log("Fetching initial story...");
        
        fetch(`${API_BASE_URL}/start`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log("Story received:", data);
                
                if (data.story) {
                    setStory(data.story);
                    setChoices(data.choices || []);
                    setStatusMessage("");
                    
                    if (data.session_id) {
                        setSessionId(data.session_id);
                    }
                    
                    // Add to game history
                    setGameHistory([{
                        story: data.story,
                        choices: data.choices
                    }]);
                } else {
                    setStatusMessage("Failed to generate the initial story.");
                }
            })
            .catch((error) => {
                console.error("Failed to fetch the initial story:", error);
                setStatusMessage(`Failed to fetch the initial story: ${error.message}`);
            })
            .finally(() => {
                setLoading(false);
            });
    }, []);

    // Function to handle player choice and fetch the next story
    const handleChoice = (choice, choiceText) => {
        if (!sessionId) {
            setStatusMessage("Session ID is missing. Please restart the game.");
            return;
        }

        setLoading(true);
        console.log(`Choice made: ${choice}, Session ID: ${sessionId}`);
        setStatusMessage("Generating the next part of the story...");
        
        // Store the previous chapter content for summary generation
        const currentChapterIndex = gameHistory.length - 1;
        const currentChapterStory = gameHistory[currentChapterIndex].story;
        
        // Add this choice to the choicesMade array
        setChoicesMade(prev => [...prev, choiceText]);
        
        fetch(`${API_BASE_URL}/choice`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                choice, 
                session_id: sessionId 
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(async data => {
            console.log("Next story received:", data);
            
            if (data.story) {
                // First, generate summary for the PREVIOUS chapter plus the choice made
                // This happens after we know the choice was successful
                const summary = await getSummaryForChapter(currentChapterStory, choiceText);
                setChapterSummaries(prev => [...prev, summary]);
                
                // Then update current story and choices for the NEW chapter
                setStory(data.story);
                setChoices(data.choices || []);
                
                // Update moral alignment if provided
                if (data.moral_alignment) {
                    setMoralAlignment(data.moral_alignment);
                }
                
                setStatusMessage("");
                
                // Add to game history
                setGameHistory(prev => [...prev, {
                    story: data.story,
                    choices: data.choices
                }]);
            } else if (data.error) {
                setStatusMessage(`Error: ${data.error}`);
            } else {
                setStatusMessage("Failed to generate the next part of the story.");
            }
        })
        .catch((error) => {
            console.error("Error processing your choice:", error);
            setStatusMessage(`Error processing your choice: ${error.message}`);
        })
        .finally(() => {
            setLoading(false);
        });
    };

    // Function to restart the game
    const restartGame = () => {
        setStory("");
        setChoices([]);
        setSessionId(null);
        setGameHistory([]);
        setChoicesMade([]);
        setChapterSummaries([]);
        setMoralAlignment("neutral");
        setStatusMessage("Starting a new game...");
        
        // Trigger the initial story fetch again
        setLoading(true);
        fetch(`${API_BASE_URL}/start`)
            .then(response => response.json())
            .then(data => {
                if (data.story) {
                    setStory(data.story);
                    setChoices(data.choices || []);
                    setStatusMessage("");
                    
                    if (data.session_id) {
                        setSessionId(data.session_id);
                    }
                    
                    setGameHistory([{
                        story: data.story,
                        choices: data.choices
                    }]);
                }
            })
            .catch(error => {
                setStatusMessage(`Failed to restart: ${error.message}`);
            })
            .finally(() => {
                setLoading(false);
            });
    };

    return (
        <div className="App">
            {/* Story Journey Sidebar */}
            <div className="sidebar">
                {/* Add moral alignment indicator */}
                <div className={`moral-indicator ${moralAlignment}`}>
                    <h3>Character Path</h3>
                    <div className="moral-meter">
                        <div className="moral-label good">Virtuous</div>
                        <div className="moral-bar">
                            <div className={`moral-fill ${moralAlignment}`}></div>
                        </div>
                        <div className="moral-label evil">Dark</div>
                    </div>
                </div>

                <h2>Your Journey</h2>
                {gameHistory.map((entry, index) => (
                    <div key={index} className="journey-entry">
                        <div className="chapter">Chapter {index + 1}</div>
                        
                        {/* Show the AI summary for completed chapters (we have a summary) */}
                        {index < chapterSummaries.length && (
                            <div className="chapter-summary">{chapterSummaries[index]}</div>
                        )}
                        
                        {/* For chapters without summary (current chapter), show raw content */}
                        {index >= chapterSummaries.length && (
                            <>
                                <div className="story-summary">{createSummary(entry.story)}</div>
                                {index < choicesMade.length && (
                                    <div className="choice-made">→ {choicesMade[index]}</div>
                                )}
                            </>
                        )}
                    </div>
                ))}
            </div>
            
            {/* Main Game Content */}
            <div className="main-content">
                <h1>AI Choice Game</h1>

                {/* Dialogue box for displaying the story */}
                <div className="dialogue-box">
                    {loading ? (
                        <p>Loading your adventure...</p>
                    ) : story ? (
                        <p>{story}</p>
                    ) : (
                        <p>Waiting for your story to begin...</p>
                    )}
                </div>

                {/* Choice buttons - dynamically rendered */}
                <div className="choice-box">
                    {!loading && choices.length > 0 ? (
                        choices.map((choice, index) => (
                            <button 
                                key={index} 
                                onClick={() => handleChoice(index + 1, choice)}
                                className="choice-button"
                                disabled={loading}
                            >
                                {choice}
                            </button>
                        ))
                    ) : loading ? (
                        <p>Loading choices...</p>
                    ) : (
                        <button onClick={restartGame} className="choice-button">
                            Start New Game
                        </button>
                    )}
                </div>

                {/* Status message */}
                {statusMessage && <div className="status-box">{statusMessage}</div>}
            </div>
        </div>
    );
}

export default App;
