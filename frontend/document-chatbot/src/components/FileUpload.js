// src/components/FileUpload.js
import React, { useState } from 'react';
import './FileUpload.css';

const FileUpload = () => {
  const [files, setFiles] = useState([]);

  const handleFileUpload = (event) => {
    const uploadedFiles = Array.from(event.target.files);
    setFiles(uploadedFiles);
  };

  return (
    <div className="file-upload">
      <h2>Upload Files</h2>
      <div className="upload-container">
        <input
          type="file"
          multiple
          id="fileInput"
          className="file-input"
          onChange={handleFileUpload}
        />
        <label htmlFor="fileInput" className="file-label">
          Select Files
        </label>
      </div>
      <div className="file-info">
        {files.length > 0 ? (
          <p>{files.length} file(s) selected</p>
        ) : (
          <p>No files selected</p>
        )}
      </div>
      {files.length > 0 && (
        <div className="file-list">
          <ul>
            {files.map((file, index) => (
              <li key={index} title={file.name}>
                {file.name}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default FileUpload;