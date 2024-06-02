import React, { useState, useRef, useEffect } from 'react';
import { FaCheckCircle } from 'react-icons/fa'; 
import './CustomDropdown.css';

const CustomDropdown = ({ collections, selectedCollection, onSelect, onDelete }) => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = React.useRef(null);

  const toggleDropdown = () => {
    setIsOpen(!isOpen);
  };

  const handleSelect = (collectionName) => {
    onSelect(collectionName);
    setIsOpen(false);
  };

  React.useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };
  
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  return (
    <div className="custom-dropdown" ref={dropdownRef}>
      <button className="dropdown-toggle" onClick={toggleDropdown}>
        
        {selectedCollection || 'Select a collection'}
      </button>
      {isOpen && (
        <div className="dropdown-menu">
          <div className="dropdown-item" onClick={() => handleSelect('')}>
            Select your collection
          </div>
          {collections.map((collection) => (
            <div key={collection.name} className="dropdown-item" onClick={() => handleSelect(collection.name)}>
              <span>{collection.name}</span>
              {collection.isIndexed && <FaCheckCircle />}
              <button 
                className="delete-button" 
                onClick={(e) => { e.stopPropagation(); onDelete(collection.name); }}
              >
                X
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default CustomDropdown;