import React from 'react';
import './App.css';
import FileUpload from './components/FileUpload';

function App() {
  return (
    <div className="App">
      <div className="left">
        <FileUpload />
      </div>
      <div className="right">
        {/* Right side content will go here */}
      </div>
    </div>
  );
}

export default App;
