// src/config.js

let baseURL = 'http://localhost:5000';

const getBaseURL = () => {
  return baseURL;
};

const setBaseURL = (url) => {
  baseURL = url;
};

export { getBaseURL, setBaseURL };