import React, { useState, useEffect } from 'react';
import axios from 'axios';
import config from '../config'; // Import your config file
import './Chatbot.css';
import CustomDropdown from './CustomDropdown'; 

import { FaEye, FaEyeSlash, FaCheckCircle } from 'react-icons/fa';

const Chatbot = ({ setFetchCollections }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [openaiKey, setOpenaiKey] = useState('');
  const [apiKeyValid, setApiKeyValid] = useState(false);
  const [isKeyRevealed, setIsKeyRevealed] = useState(false);
  const [showAsterisks, setShowAsterisks] = useState(true);
  const [selectedCollection, setSelectedCollection] = useState('');
  const [collections, setCollections] = useState([]);
  const [isGeneratingIndex, setIsGeneratingIndex] = useState(false);
  const [loading, setLoading] = useState(false);
  
  useEffect(() => {
    const storedKey = localStorage.getItem('openaiKey');
    if (storedKey) {
      // setOpenaiKey(storedKey);
      setApiKeyValid(true);
    }
    fetchCollections();
    setFetchCollections(fetchCollections);
  }, []);

  const eraseApiKey = () => {
    localStorage.removeItem('openaiKey'); // Remove the key from local storage
    setApiKeyValid(false);                // Reset validation state
    setOpenaiKey('');                     // Clear the input field
  };

  const validateApiKey = async () => {
    try {
      const response = await axios.post(`${config.apiUrl}/validate_openai_key`, { api_key: openaiKey });
      if (response.status === 200) {
        setApiKeyValid(true);
        localStorage.setItem('openaiKey', openaiKey); // Store the key in local storage
        setOpenaiKey(''); // Clear the input field
        alert('Valid API key! You can now send messages to the chatbot.');
      }
    } catch (error) {
      setApiKeyValid(false);
      alert('Invalid API key! Please enter a valid API key.');
    }
  };

  const fetchCollections = async () => {
    try {
      const response = await axios.get(`${config.apiUrl}/get_collections`);
      if (response.data.status === 200) {
        setCollections(response.data.collections);
      } else if (response.status === 500) {
        alert('Failed to connect to MongoDB. Please check.');
        setCollections([]);
      }
    } catch (error) {
      alert('Failed to fetch collections. Please try again.');
      setCollections([]);
    }
  };

  useEffect(() => {
    fetchCollections();
    setFetchCollections(fetchCollections);
  }, []);

  const handleSendMessage = async () => {
    if (input.trim() === '') return;
    
    const userMessage = { text: input, sender: 'user' };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const formData = new FormData();
      formData.append('message', input);
      const response = await axios.post(`${config.apiUrl}/chat_with_agent`, formData, {
        headers: {
            'Content-Type': 'multipart/form-data'
        },
        timeout: 60000
    }); 
    
      if (response.status === 200) {
        const botMessage = { text: response.data[0].response, sender: 'bot' };
       
        setMessages((prev) => [...prev, botMessage]);
      }
    } catch (error) {
      // console.error("Error while chatting with the agent:", error);
      const errorMessage = { text: 'Error: Unable to get response from the bot.', sender: 'bot' };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
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

  const handleCollectionChange = (event) => {
    setSelectedCollection(event.target.value);
  };

  const handleGenerateIndex = async () => {
    if (selectedCollection === '') {
      alert('Please select a collection first.');
      return;
    }
    setIsGeneratingIndex(true);
    try {
      const formData = new FormData();
      formData.append('collection_name', selectedCollection)
      const response = await axios.post(`${config.apiUrl}/generate_index`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        timeout: 60000
      });
      if (response.status === 200) {
        setIsGeneratingIndex(false);
        alert('Index generated successfully!');
      }
    } catch (error) {
      if (error.response) {
        const errorMessage = error.response.data.detail;
        alert(`Error: ${errorMessage}`);
      } else if (error.request) {
        // The request was made but no response was received
        alert('Error: No response received from the server.');
      } else {
        // Something happened in setting up the request that triggered an Error
        alert(`Error: ${error.message}`);
      }
    }
  };
  
  const handleDeleteCollection = async (collection) => {
    if (collection === '') {
        alert('Please select a collection first.');
        return;
    }
      try {
        const response = await axios.delete(`${config.apiUrl}/delete_collection`, {
          params: {
            collection_name: collection
          },
          timeout: 3000
        });
        if (response.status === 200) {
            alert('Collection deleted successfully!');
            setCollections(collections.filter(c => c !== collection));
            setSelectedCollection('');
        }
    } catch (error) {
        if (error.response) {
          alert(`Error: ${error.response.data.detail}`);
        } else {
        alert('Failed to delete collection. Please try again.');
      }
    }
};

  return (
    <div>
      <div className="openai-key-container">
        <div className="input-with-button">
          <input
            type={showAsterisks ? 'password' : 'text'}
            value={openaiKey}
            onChange={handleOpenaiKeyChange}
            placeholder="Enter your OpenAI key..."
            className="input-field"
            required
          />
          <button onClick={handleToggleKeyVisibility} className="reveal-button">
            {showAsterisks ? <FaEyeSlash /> : <FaEye />}
          </button>
          <button onClick={handleSubmitKey} className="submit-button">Submit</button>
          <button onClick={eraseApiKey} className="erase-btn">Erase Key</button>

          {apiKeyValid && <FaCheckCircle className="check-icon" />}
        </div>
      </div>
      <div className="chatbot-container">
        <div className="collection-dropdown">
          <CustomDropdown
            collections={collections}
            selectedCollection={selectedCollection}
            onSelect={setSelectedCollection}
            onDelete={handleDeleteCollection}
          />
          <button 
            onClick={handleGenerateIndex} 
            className="button generate-button" 
            disabled={!apiKeyValid || isGeneratingIndex}
          >
            {isGeneratingIndex ? 'Generating...' : 'Generate Index'}
          </button>
        </div>
        <div className="chat-window">
          {messages.map((message, index) => (
            <div key={index} className={`message ${message.sender}`}>
              {message.sender === 'user' ? (
                <div className="user-message">{message.text}</div>
              ) : (
                <div className="bot-message">{message.text}</div>
              )}
            </div>
          ))}
          {loading && <div className="message bot"><div className="bot-message">...</div></div>}
        </div>
        <div className="input-container">
          <input
            type="text"
            value={input}
            onChange={handleInputChange}
            onKeyPress={handleKeyPress}
            placeholder="Type a message..."
            disabled={!apiKeyValid}  // Disable input when API key is invalid
          />
          <button 
            onClick={handleSendMessage} 
            className="button send-button"
            disabled={!apiKeyValid}  // Conditionally disable the send button
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
};

export default Chatbot;