// src/components/FileUpload.js
import React, { useState } from 'react';
import './FileUpload.css';

const FileUpload = () => {
  const [fileNames, setFileNames] = useState([]);

  const handleFileUpload = (event) => {
    const files = Array.from(event.target.files);
    setFileNames(files.map(file => file.name));
    console.log(files);
  };

  return (
    <div className="file-upload">
      <h2>Upload Files</h2>
      <input type="file" multiple onChange={handleFileUpload} />
      {fileNames.length > 0 && (
        <div className="file-list">
          <h3>Files to be uploaded:</h3>
          <ul>
            {fileNames.map((name, index) => (
              <li key={index}>{name}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default FileUpload;
