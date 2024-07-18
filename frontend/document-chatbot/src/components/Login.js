import React from 'react';
import { AuthForm } from './AuthForm';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import config from '../config'; 


export const Login = () => {
    const navigate = useNavigate();

    const handleLogin = async (e) => {
        e.preventDefault();
        const { username, password } = e.target.elements;
      
        try {
            const response = await axios.post(`${config.apiUrl}/login`, {
                username: username.value,
                password: password.value,
              }, {
                headers: {
                  'Content-Type': 'application/x-www-form-urlencoded', // replace with the expected content type
                },
              });

          if (response.status !== 200) {
            alert(response.data.error); // show the error message
            return;
          }
          const data = response.data;
          localStorage.setItem('token', data.access_token); // save the token
          navigate('/home');
        } catch (error) {
          console.error(error);
          alert('Failed to login due to invalid credentials');} 
      };


  return <AuthForm title="Login" onSubmit={handleLogin} submitText="Login" />;
};