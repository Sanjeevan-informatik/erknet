// src/Login.js

import React, { useState } from 'react';
import axios from 'axios';
import { useHistory } from 'react-router-dom';
import { getBaseURL, setBaseURL } from '../../config';
import './Login.css';

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');
  const baseURL = getBaseURL(); // Access baseURL from the configuration module
  const history = useHistory();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post(`${baseURL}/login`, {
        username: username,
        password: password
      });
      setMessage(response.data.message);
      history.push('/dashboard');
    } catch (error) {
      setMessage(error.response.data.error);
    }
  };

  const handleBaseURLChange = (e) => {
    setBaseURL(e.target.value); // Update baseURL in the configuration module
  };

  return (
    <div className="login-container">
      <h2>Login</h2>
      <form onSubmit={handleSubmit} className="login-form">
        <div className="form-group">
          <label htmlFor="username" className="form-label">Username:</label>
          <input
            type="text"
            id="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="form-input"
          />
        </div>
        <div className="form-group">
          <label htmlFor="password" className="form-label">Password:</label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="form-input"
          />
        </div>
        <div className="form-group">
          <label htmlFor="baseURL" className="form-label">backend host address URL:</label>
          <input
            type="text"
            id="baseURL"
            value={baseURL}
            onChange={handleBaseURLChange}
            className="form-input"
          />
        </div>
        <button type="submit" className="submit-button">Login</button>
      </form>
      {message && <div className="message">{message}</div>}
    </div>
  );
};

export default Login;
