import React, { useState } from 'react';
import { Lock, ShieldCheck, User } from 'lucide-react';
import './index.css';

function Login({ setToken }) {
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('supersecret');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);

      const response = await fetch('http://localhost:8000/token', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Invalid credentials or unauthorized access');
      }

      const data = await response.json();
      setToken(data.access_token);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-container" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh' }}>
      <div className="glass-panel" style={{ maxWidth: '400px', width: '100%', textAlign: 'center', padding: '40px' }}>
        <ShieldCheck size={64} color="var(--accent-cyan)" style={{ marginBottom: '24px' }} />
        <h2 style={{ marginBottom: '8px' }}>SOC Authentication</h2>
        <p style={{ color: 'var(--text-secondary)', marginBottom: '32px' }}>Enter your Enterprise ID to access the Omni-Analyzer.</p>
        
        <form onSubmit={handleLogin} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div style={{ position: 'relative' }}>
            <User size={20} color="var(--text-secondary)" style={{ position: 'absolute', left: '12px', top: '14px' }} />
            <input 
              type="text" 
              className="input-field" 
              placeholder="Username" 
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              style={{ paddingLeft: '40px', width: '100%' }}
              required
            />
          </div>
          
          <div style={{ position: 'relative' }}>
            <Lock size={20} color="var(--text-secondary)" style={{ position: 'absolute', left: '12px', top: '14px' }} />
            <input 
              type="password" 
              className="input-field" 
              placeholder="Password" 
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              style={{ paddingLeft: '40px', width: '100%' }}
              required
            />
          </div>

          {error && <p style={{ color: '#ef4444', fontSize: '0.9rem', marginTop: '8px' }}>{error}</p>}

          <button type="submit" className="glow-btn" style={{ marginTop: '16px', display: 'flex', justifyContent: 'center' }} disabled={isLoading}>
            {isLoading ? 'Authenticating...' : 'Secure Login'}
          </button>
        </form>
      </div>
    </div>
  );
}

export default Login;
