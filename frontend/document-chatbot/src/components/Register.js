import React from 'react';
import { AuthForm } from './AuthForm';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import config from '../config';

export const Register = () => {
    const navigate = useNavigate();

    const handleRegister = async (e) => {
        e.preventDefault();
        const { username, password } = e.target.elements;

        try {
            const response = await axios.post(`${config.apiUrl}/register`, {
                username: username.value, 
                password: password.value,
              });
        
            alert('User created successfully');
            navigate('/login');
          } catch (error) {
            const errorMessage =  error.response.data.detail

            alert(`Error ${errorMessage}`);
            // console.error('Error:', error);
          }
        
    };

  return <AuthForm title="Register" onSubmit={handleRegister} submitText="Register" />;
};