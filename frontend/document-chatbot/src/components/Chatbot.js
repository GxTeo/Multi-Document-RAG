// src/components/Chatbot.js
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import config from '../config'; // Import your config file
import './Chatbot.css';
import { FaEye, FaEyeSlash } from 'react-icons/fa'; // Import eye icons from react-icons library
import { FaCheckCircle } from 'react-icons/fa'; // Import check circle icon from react-icons library

const Chatbot = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [openaiKey, setOpenaiKey] = useState('');
  const [apiKeyValid, setApiKeyValid] = useState(false);
  const [isKeyRevealed, setIsKeyRevealed] = useState(false);
  const [showAsterisks, setShowAsterisks] = useState(true);



  const validateApiKey = async (key) => {
    try {
      const response = await axios.post(`${config.apiUrl}/validate_openai_key`, { api_key: openaiKey });
      if (response.status === 200) {
        setApiKeyValid(true);
        alert('Valid API key! You can now send messages to the chatbot.');
        // localStorage.setItem('openaiKey', key); // Store valid API key in local storage
      }
    } catch (error) {
      if (error.response.status === 400) {
        setApiKeyValid(false);
        alert('Invalid API key! Please enter a valid API key.');
      }
      else {
        setApiKeyValid(false);
        alert('Invalid API key! Please enter a valid API key.');
      }
    }
  };

  const handleSendMessage = () => {
    if (input.trim() !== '' && apiKeyValid) {
      // Send message
    } else {
      console.error('Invalid API key or empty message');
    }
  };

  const handleInputChange = (event) => {
    setInput(event.target.value);
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter') {
      handleSendMessage();
    }
  };

  const handleOpenaiKeyChange = (event) => {
    setOpenaiKey(event.target.value);
  };

  const handleSubmitKey = () => {
    validateApiKey();
  };

  const handleToggleKeyVisibility = () => {
    if (isKeyRevealed) {
      setShowAsterisks(true);
    } else {
      setShowAsterisks((prev) => !prev);
    }
    setIsKeyRevealed((prev) => !prev);
  };

  return (
    <div>
      <div className="openai-key-container">
        <div className="input-with-button">
          <input
            type={showAsterisks ? 'password' : 'text'} // Toggle input type based on showAsterisks state
            value={openaiKey}
            onChange={handleOpenaiKeyChange}
            placeholder="Enter your OpenAI key..."
            className="input-field"
            required
          />
          <button onClick={handleToggleKeyVisibility} className="reveal-button">
            {isKeyRevealed ? (showAsterisks ? <FaEyeSlash /> : <FaEye />) : <FaEye />} {/* Toggle eye icon based on key visibility */}
          </button>
          <button onClick={handleSubmitKey} className="submit-button">Submit</button>
          {apiKeyValid && <FaCheckCircle className="check-icon" />} {/* Display check icon if API key is valid */}

        </div>
      </div>
      <div className="chatbot-container">
        <div className="chat-window">
          {/* Chat messages */}
        </div>
        <div className="input-container">
          <input
            type="text"
            value={input}
            onChange={handleInputChange}
            onKeyPress={handleKeyPress}
            placeholder="Type a message..."
            style={{ width: '80%', padding: '10px', borderRadius: '8px' }}
          />
          <button onClick={handleSendMessage} className="send-button">Send</button>
        </div>
      </div>
    </div>
  );
};

export default Chatbot;
