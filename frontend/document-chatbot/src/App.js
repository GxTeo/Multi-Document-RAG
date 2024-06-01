// src/App.js
import React, { useState } from 'react';
import './App.css';
import FileUpload from './components/FileUpload';
import Chatbot from './components/Chatbot';

function App() {
  const [collections, setCollections] = useState([]);

  const handleNewCollection = (collectionName) => {
    setCollections([...collections, collectionName]);
  };

  return (
    <div className="App">
      <div className="left">
        <FileUpload onNewCollection={handleNewCollection} />
      </div>
      <div className="right">
        <Chatbot collections={collections} />
      </div>
    </div>
  );
}

export default App;