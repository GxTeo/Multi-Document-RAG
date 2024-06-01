import React, { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import './FileUpload.css';

const FileUpload = () => {
  const [files, setFiles] = useState([]);
  const [collectionName, setCollectionName] = useState('');
  const [isNamePromptVisible, setIsNamePromptVisible] = useState(false);

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

  const handleConfirmName = () => {
    // Regular expression to allow only alphanumeric characters and underscores
    const regex = /^[a-zA-Z0-9_]+$/;
  
    if (!regex.test(collectionName)) {
      alert('Collection name can only contain alphanumeric characters and underscores.');
    } else {
      // Proceed with submitting the file collection with the provided name
      setIsNamePromptVisible(false);
      setCollectionName('');
      setFiles([]);
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
