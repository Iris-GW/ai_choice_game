import React, { useState, useEffect } from 'react';
import './App.css'; // Import the CSS file

function App() {
    const [story, setStory] = useState("");
    const [choices, setChoices] = useState([]);
    const [statusMessage, setStatusMessage] = useState("Waiting for the story to load..."); // Initial status message

    // Fetch the initial story when the component mounts
    useEffect(() => {
        console.log("Fetching initial story...");  // Log when fetching starts
        fetch('/start')
            .then(response => response.json())
            .then(data => {
                console.log("Story received:", data);  // Log the received data
                if (data.story) {
                    setStory(data.story);
                    setChoices(data.choices || []); // Update choices based on the response
                    setStatusMessage(""); // Clear any previous error messages
                } else {
                    setStatusMessage("Failed to generate the initial story."); // Handle error
                }
            })
            .catch((error) => {
                console.error("Failed to fetch the initial story:", error); // Log the network error
                setStatusMessage("Failed to fetch the initial story."); // Network error handling
            });
    }, []); // Empty dependency array ensures this runs only once on mount

    // Function to handle player choice and fetch the next story
    const handleChoice = (choice) => {
        console.log(`Choice made: ${choice}`);  // Log the choice made
        setStatusMessage("Generating the next part of the story..."); // Show status message while waiting for AI response
        fetch('/choice', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ choice })  // Send choice (1, 2, 3, or 4)
        })
        .then(response => response.json())
        .then(data => {
            console.log("Next story received:", data);  // Log the next part of the story received
            if (data.story) {
                setStory(data.story);  // Update story with new content
                setChoices(data.choices || []); // Update choices with the new choices from the response
                setStatusMessage("");  // Clear any error or loading message
            } else {
                setStatusMessage("Failed to generate the next part of the story."); // Handle error
            }
        })
        .catch((error) => {
            console.error("Error processing your choice:", error); // Log the network error
            setStatusMessage("Error processing your choice."); // Network error handling
        });
    };

    return (
        <div className="App">
            <h2 className="character-name">Game Story</h2>

            {/* Dialogue box for displaying the story */}
            <div className="dialogue-box">
                <p>{story}</p>
            </div>

            {/* Choice buttons - dynamically rendered */}
            <div className="choice-box">
                {choices.map((choice, index) => (
                    <button 
                        key={index} 
                        onClick={() => handleChoice(index + 1)}
                        className="choice-button"
                    >
                        {choice}
                    </button>
                ))}
            </div>

            {/* Status message for showing any error or loading messages */}
            {statusMessage && <div className="status-box">{statusMessage}</div>}
        </div>
    );
}

export default App;
