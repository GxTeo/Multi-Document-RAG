import React, { useState, useRef, useEffect } from 'react';
import './CustomDropdown.css';

const CustomDropdown = ({ collections, selectedCollection, onSelect, onDelete }) => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);

  const toggleDropdown = () => {
    setIsOpen(!isOpen);
  };

  const handleSelect = (collection) => {
    onSelect(collection);
    setIsOpen(false);
  };

  useEffect(() => {
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
            Select a collection
          </div>
          {collections.map((collection, index) => (
            <div key={index} className="dropdown-item" onClick={() => handleSelect(collection)}>
              <span>{collection}</span>
              <button className="delete-button" onClick={(e) => { e.stopPropagation(); onDelete(collection); }}>X</button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default CustomDropdown;