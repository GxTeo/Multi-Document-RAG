// src/components/FileUpload.js
import React, { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';
import config from '../config';
import './FileUpload.css';

const FileUpload = ({ fetchCollections }) => {
  const [files, setFiles] = useState([]);
  const [collectionName, setCollectionName] = useState('');
  const [isNamePromptVisible, setIsNamePromptVisible] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [completedUploads, setCompletedUploads] = useState(0);
  const token = localStorage.getItem('token');


  const sendFilesToBackend = async (collectionName, files = []) => {  
    try {
      for (const file of files) {
        const formData = new FormData();
        formData.append('collection_name', collectionName);
        formData.append('files', file);
    
        const response = await axios.post(`${config.apiUrl}/upload_files`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
            'Authorization': `Bearer ${token}`,
          },
          timeout: 100000,
        });

        if (response.status === 200) {
          setCompletedUploads(prevCount => prevCount + 1);
        }
        else if (response.status !== 200) {
          alert('Failed to upload file: ' + file.name);
          throw new Error('Failed to upload file: ' + file.name);
        }
      }
    
      alert('Files uploaded successfully');
      fetchCollections();
    } catch (error) {
      // Handle specific error responses from the backend
      if (error.response) {
        if (error.response.status === 400) {
          alert('Invalid file type. Only PDF and DOCX files are allowed.');
        } else if (error.response.status === 500) {
          alert('Unable to connect to the database.');
        } else {
          alert(`Error: ${error.response.data.detail}`);
        }
      } else {
        alert('An unexpected error occurred.');
      }
      console.error('Error uploading files:', error);
  };
  setCompletedUploads(0);
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

  const handleCancel = () => {
    setIsNamePromptVisible(false);
  };

  const handleConfirmName = async () => {
    if (collectionName.trim() === '') {
      alert('Please provide a name for the file collection.');
    } else {
      try {
        setIsLoading(true);
        await sendFilesToBackend(collectionName, files);
        setIsNamePromptVisible(false);
        setCollectionName('');
        setFiles([]);
        setIsLoading(false);
      } catch (error) {
        console.error('Error uploading files:', error);
        alert('There was an error uploading the files. Please try again.');
        setIsLoading(false);
      }
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop });

  return (
    <div className="file-upload-container">
      {isLoading && (
        <div className="upload-status">
          <p>Upload progress: {completedUploads} / {files.length}</p>
          <div className="loading-icon"></div>
        </div>
      )}
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
      {!isNamePromptVisible && (
        <button onClick={handleSubmit} className="submit-button">Submit</button>
      )}      
      {isNamePromptVisible && (
        <div className="name-prompt">
          <input
            type="text"
            value={collectionName}
            onChange={(e) => setCollectionName(e.target.value)}
            placeholder="Enter collection name..."
            className="name-input"
          />
          <div className="button-group">
            <button onClick={handleConfirmName} className="confirm-button">Confirm</button>
            <button onClick={handleCancel} className="cancel-button">Cancel</button>
          </div>
        </div>
      )}
    </div>
  );
};

export default FileUpload;