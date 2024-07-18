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
        
            if (response.status !== 200) {
              alert(response.data.detail); // show the error message
              return;
            }
        
            alert('User created successfully');
          } catch (error) {
            alert('Failed to register');
            console.error('Error:', error);
          }
        navigate('/login');
    };

  return <AuthForm title="Register" onSubmit={handleRegister} submitText="Register" />;
};