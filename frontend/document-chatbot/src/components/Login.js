// src/components/Login.js
import React from 'react';
import { AuthForm } from './AuthForm';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import config from '../config';
import { useAuth } from '../context/AuthContext';

export const Login = () => {
    const navigate = useNavigate();
    const { login } = useAuth();

    const handleLogin = async (e) => {
        e.preventDefault();
        const { username, password } = e.target.elements;
      
        try {
            const response = await axios.post(`${config.apiUrl}/login`, {
                username: username.value,
                password: password.value,
              }, {
                headers: {
                  'Content-Type': 'application/x-www-form-urlencoded',
                },
              });

          if (response.status !== 200) {
            alert(response.data.error);
            return;
          }
          const data = response.data;
          login(data.access_token); // Store token in context
          navigate('/home');
        } catch (error) {
          console.error(error);
          alert('Failed to login due to invalid credentials');
        } 
    };

    return <AuthForm title="Login" onSubmit={handleLogin} submitText="Login" />;
};