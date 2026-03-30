import React, { useState } from 'react';
import Login from './Login';
import Dashboard from './Dashboard';
import './index.css';

function App() {
  const [token, setToken] = useState(null);

  const handleLogout = () => {
    setToken(null);
  };

  if (!token) {
    return <Login setToken={setToken} />;
  }

  return <Dashboard token={token} onLogout={handleLogout} />;
}

export default App;
