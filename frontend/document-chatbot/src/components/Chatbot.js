// src/components/Chatbot.js
import React, { useState } from 'react';
import './Chatbot.css';

const Chatbot = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [openaiKey, setOpenaiKey] = useState('');

  const handleSendMessage = () => {
    if (input.trim() !== '' && openaiKey.trim() !== '') {
      setMessages([...messages, { sender: 'user', text: input }]);
      setInput('');
      // Simulate bot response
      setTimeout(() => {
        setMessages((prevMessages) => [
          ...prevMessages,
          { sender: 'bot', text: 'This is a bot response.' },
        ]);
      }, 500);
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

  return (
    <div>
      <div className="openai-key-container">
        <input
          type="text"
          value={openaiKey}
          onChange={handleOpenaiKeyChange}
          placeholder="Enter your OpenAI key..."
          style={{ width: '100%', padding: '10px', borderRadius: '8px', marginBottom: '10px' }}
          required
        />
      </div>
      <div className="chatbot-container">
        <div className="chat-window">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`message ${message.sender === 'user' ? 'user-message' : 'bot-message'}`}
            >
              {message.text}
            </div>
          ))}
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
          <button onClick={handleSendMessage}>Send</button>
        </div>
      </div>
    </div>
  );
};

export default Chatbot;
