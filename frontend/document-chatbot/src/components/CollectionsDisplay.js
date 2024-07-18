import React, { useState, useEffect } from 'react';
import axios from 'axios';
import config from '../config'; // Ensure this contains the correct API URLs
import './CollectionsDisplay.css';

const CollectionsDisplay = () => {
  const [collections, setCollections] = useState({});
  const [openCollections, setOpenCollections] = useState({});
  const token = localStorage.getItem('token');

  useEffect(() => {
    fetchCollections();
  }, []); // Dependency array is empty to only run on mount

  const fetchCollections = async () => {
    try {
      const response = await axios.get(`${config.apiUrl}/display_collections`, {
        headers: {
          'Authorization': `Bearer ${token}` // include the token in the Authorization header
        }
      });      
      if (response.status === 200) {
        setCollections(response.data);
        // Initialize all collections to be collapsed
        const initialOpenState = Object.keys(response.data).reduce((acc, cur) => {
          acc[cur] = false;
          return acc;
        }, {});
        setOpenCollections(initialOpenState);
      } else {
        throw new Error('Failed to fetch collections');
      }
    } catch (error) {
      console.error('Error fetching collections:', error);
      alert('There was an error fetching the collections. Please try again.');
    }
  };

  const toggleCollection = (collectionName) => {
    setOpenCollections(prev => ({
      ...prev,
      [collectionName]: !prev[collectionName]
    }));
  };

  return (
    <div className="collections-container">
      {Object.keys(collections).length > 0 ? (
        Object.keys(collections).map((collectionName) => (
          <div key={collectionName}>
            <h3 onClick={() => toggleCollection(collectionName)} style={{ cursor: 'pointer' }}>
              {collectionName} {openCollections[collectionName] ? '▼' : '►'}
            </h3>
            {openCollections[collectionName] && (
              <ul>
                {collections[collectionName].map((fileName, index) => (
                  <li key={index}>{fileName}</li>
                ))}
              </ul>
            )}
          </div>
        ))
      ) : (
        <p>No collections available. Please upload files.</p>
      )}
    </div>
  );
};

export default CollectionsDisplay;