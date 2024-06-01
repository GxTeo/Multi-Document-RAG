// src/components/FileUpload.js
import React, { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';
import config from '../config';
import './FileUpload.css';

const FileUpload = ({ onNewCollection }) => {
  const [files, setFiles] = useState([]);
  const [collectionName, setCollectionName] = useState('');
  const [isNamePromptVisible, setIsNamePromptVisible] = useState(false);

  const sendFilesToBackend = async () => {
    const formData = new FormData();
    formData.append('collection_name', collectionName);
    files.forEach((file) => formData.append('files', file));

    const response = await axios.post(`${config.apiUrl}/upload_files`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    if (response.status !== 200) {
      alert('Failed to upload files');
      throw new Error('Failed to upload files');
    }
  };

  const onDrop = (acceptedFiles) => {
    setFiles([...files, ...acceptedFiles]);
  };

  const handleRemoveFile = (index) => {
    setFiles(files.filter((_, i) => i !== index));
  };

  const handleSubmit = () => {
    if (files.length === 0) {
      alert('Please select at least one file.');
    } else {
      setIsNamePromptVisible(true);
    }
  };

  const handleConfirmName = async () => {
    if (collectionName.trim() === '') {
      alert('Please provide a name for the file collection.');
    } else {
      try {
        await sendFilesToBackend();
        onNewCollection(collectionName);
        setIsNamePromptVisible(false);
        setCollectionName('');
        setFiles([]);
      } catch (error) {
        console.error('Error uploading files:', error);
        alert('There was an error uploading the files. Please try again.');
      }
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop });

  return (
    <div className="file-upload-container">
      <div {...getRootProps({ className: 'dropzone' })}>
        <input {...getInputProps()} />
        <div className="upload-icon">📂</div>
        <p>Click to upload or drag and drop</p>
        <p className="file-types">PDF and DOCX </p>
        <p className="file-count">{files.length} file(s) selected</p>
      </div>
      {files.length > 0 && (
        <div className="file-list">
          <ul>
            {files.map((file, index) => (
              <li key={index} title={file.name} className="file-item">
                <span className="file-name">{file.name}</span>
                <button
                  className="remove-file-button"
                  onClick={() => handleRemoveFile(index)}
                >
                  &times;
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}
      <button onClick={handleSubmit} className="submit-button">Submit</button>
      {isNamePromptVisible && (
        <div className="name-prompt">
          <input
            type="text"
            value={collectionName}
            onChange={(e) => setCollectionName(e.target.value)}
            placeholder="Enter collection name..."
            className="name-input"
          />
          <button onClick={handleConfirmName} className="confirm-button">Confirm</button>
        </div>
      )}
    </div>
  );
};

export default FileUpload;