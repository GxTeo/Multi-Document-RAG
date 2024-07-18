// src/App.js
import React, { useRef, useState, useCallback } from 'react';
import { Link } from 'react-router-dom';

import './App.css';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import { Login } from './components/Login';
import { Register } from './components/Register';

import Logout from './components/Logout';
import FileUpload from './components/FileUpload';
import CollectionsDisplay from './components/CollectionsDisplay'; // Import the CollectionsDisplay component
import Chatbot from './components/Chatbot';

function App() {
  const fetchCollectionsRef = useRef(null);
  const [updateToggle, setUpdateToggle] = useState(false); // To trigger re-fetches
  const token = localStorage.getItem('token');

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
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route
          path="/home"
          element={
            <div className="App">
              <div className="logout-container" style={{ position: 'absolute', top: 0, right: 0, padding: '20px' }}>
                <Logout />
              </div>
              <div className="left">
                <FileUpload fetchCollections={handleFetchCollections} />
                <CollectionsDisplay key={updateToggle} />
              </div>
              <div className="right">
                <Chatbot
                  setFetchCollections={setFetchCollections}
                  handleFetchCollections={handleFetchCollections}
                />
              </div>
            </div>
          }
        />
        <Route
          path="/"
          element={
            <div className="welcome-container">
              <h1>Welcome to Multi-Doc-RAG</h1>
              <nav className="navigation-links">
                <Link to="/login" className="link">Login</Link>
                <span> | </span>
                <Link to="/register" className="link">Register</Link>
              </nav>
            </div>
          }
        />
      </Routes>
    </Router>
  );
}
export default App;