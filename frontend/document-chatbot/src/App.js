import React, { useState, useEffect } from 'react';
import './App.css';
import FileUpload from './components/FileUpload';
import Chatbot from './components/Chatbot';

function App() {
  const [collections, setCollections] = useState(() => {
    const savedCollections = localStorage.getItem('collections');
    return savedCollections ? JSON.parse(savedCollections) : [];
  });

  useEffect(() => {
    localStorage.setItem('collections', JSON.stringify(collections));
  }, [collections]);

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