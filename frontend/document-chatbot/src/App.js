// src/App.js
import React, { useState } from 'react';
import './App.css';
import FileUpload from './components/FileUpload';
import Chatbot from './components/Chatbot';

function App() {
  return (
    <div className="App">
      <div className="left">
        <FileUpload />
      </div>
      <div className="right">
        <Chatbot />
      </div>
    </div>
  );
}

export default App;