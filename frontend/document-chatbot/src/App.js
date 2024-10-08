// src/App.js
import React, { useRef, useState, useCallback } from 'react';
import { Link, Navigate } from 'react-router-dom';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Login } from './components/Login';
import { Register } from './components/Register';
import Logout from './components/Logout';
import FileUpload from './components/FileUpload';
import CollectionsDisplay from './components/CollectionsDisplay';
import Chatbot from './components/Chatbot';
import './App.css';

function AppContent() {
  const { token } = useAuth();
  const fetchCollectionsRef = useRef(null);
  const [updateToggle, setUpdateToggle] = useState(false);

  const ProtectedRoute = ({ children }) => {
    return token ? children : <Navigate to="/" />;
  };

  const setFetchCollections = (fetchCollectionsFunction) => {
    fetchCollectionsRef.current = fetchCollectionsFunction;
  };

  const handleFetchCollections = useCallback(() => {
    if (fetchCollectionsRef.current) {
      fetchCollectionsRef.current();
      setUpdateToggle(prev => !prev);
    }
  }, []);

  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route
        path="/home"
        element={
          <ProtectedRoute>
            <div className="App">
              <div className="logout-container" style={{ position: 'absolute', top: 0, right: 0, padding: '20px' }}>
                <Logout />
              </div>
              <div className="left">
                <FileUpload fetchCollections={handleFetchCollections} token={token} />
                <CollectionsDisplay key={updateToggle} token={token} />
              </div>
              <div className="right">
                <Chatbot
                  setFetchCollections={setFetchCollections}
                  handleFetchCollections={handleFetchCollections}
                  token={token}
                />
              </div>
            </div>
          </ProtectedRoute>
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
  );
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <AppContent />
      </Router>
    </AuthProvider>
  );
}

export default App;