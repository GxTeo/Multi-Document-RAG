// src/App.js
import React, { useRef, useState, useCallback } from 'react';
import './App.css';
import FileUpload from './components/FileUpload';
import CollectionsDisplay from './components/CollectionsDisplay'; // Import the CollectionsDisplay component
import Chatbot from './components/Chatbot';

function App() {
  const fetchCollectionsRef = useRef(null);
  const [updateToggle, setUpdateToggle] = useState(false); // To trigger re-fetches

  const setFetchCollections = (fetchCollectionsFunction) => {
    fetchCollectionsRef.current = fetchCollectionsFunction;
  };

  // Wrapper around fetchCollections to allow forcing update from any component
  const handleFetchCollections = useCallback(() => {
    if (fetchCollectionsRef.current) {
      fetchCollectionsRef.current();
      setUpdateToggle(prev => !prev); // Toggle to force rerender
    }
  }, []);

  return (
    <div className="App">
      <div className="left">
        <FileUpload fetchCollections={handleFetchCollections} />
        <CollectionsDisplay key={updateToggle} />
      </div>
      <div className="right">
      <Chatbot setFetchCollections={setFetchCollections} handleFetchCollections={handleFetchCollections} />      
      </div>
    </div>
  );
}

export default App;