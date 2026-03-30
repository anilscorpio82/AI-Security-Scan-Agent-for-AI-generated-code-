import React, { useState } from 'react';
import { Shield, ShieldAlert, FileSearch, Code, Bug } from 'lucide-react';
import './index.css';

function App() {
  const [repoPath, setRepoPath] = useState('/Users/anilp.singh/.gemini/antigravity/scratch/enterprise_ai_sec/tests/vulnerable_repo');
  const [isScanning, setIsScanning] = useState(false);
  const [report, setReport] = useState(null);
  const [error, setError] = useState(null);

  const startScan = async () => {
    setIsScanning(true);
    setReport(null);
    setError(null);

    try {
      // Simulate real delay so the user can enjoy the premium scanning animation
      await new Promise(r => setTimeout(r, 1500));
      
      const response = await fetch('http://localhost:8000/scan/repo', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ repo_path: repoPath })
      });
      
      if (!response.ok) {
        throw new Error(`Backend Error ${response.status}: Make sure FastAPI is running.`);
      }
      
      const data = await response.json();
      setReport(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsScanning(false);
    }
  };

  return (
    <div className="app-container">
      <header className="header">
        <h1>Omni-Analyzer</h1>
        <p>Enterprise AI Security & Compliance Review Agent</p>
      </header>

      <main>
        {!isScanning && !report && (
          <div className="glass-panel" style={{ textAlign: 'center', maxWidth: '600px', margin: '0 auto' }}>
            <Shield size={64} color="var(--accent-cyan)" style={{ marginBottom: '24px' }} />
            <h2 style={{ marginBottom: '16px' }}>Zero-Trust Code Scanning</h2>
            <p style={{ color: 'var(--text-secondary)', marginBottom: '32px' }}>
              Drop a local repository path to initiate a holistic security review, complete with Presidio PII redaction and PCI-DSS compliance mapping.
            </p>
            
            <input 
              type="text" 
              className="input-field" 
              placeholder="/absolute/path/to/repo" 
              value={repoPath}
              onChange={(e) => setRepoPath(e.target.value)}
            />
            
            <button className="glow-btn" onClick={startScan} disabled={!repoPath}>
              <FileSearch size={20} />
              Analyze Codebase
            </button>
          </div>
        )}

        {isScanning && (
          <div className="scanning-indicator">
            <div className="pulse-circle">
              <Shield size={40} color="white" />
            </div>
            <h2>Running AI Agents...</h2>
            <p style={{ color: 'var(--accent-cyan)', marginTop: '16px', lineHeight: '1.8' }}>
               ✓ Cloning & Gathering Context<br/>
               ✓ Redacting PII via Gateway<br/>
               ⟳ Mapping Compliance Violations
            </p>
          </div>
        )}

        {error && (
          <div className="glass-panel threat-card critical" style={{ maxWidth: '600px', margin: '0 auto' }}>
            <h3><ShieldAlert color="#ef4444" /> Scan Failed</h3>
            <p>{error}</p>
            <button className="glow-btn" onClick={() => setError(null)} style={{ marginTop: '16px' }}>Go Back</button>
          </div>
        )}

        {report && report.status === "failed" && (
           <div className="glass-panel threat-card critical" style={{ maxWidth: '600px', margin: '0 auto' }}>
              <h3><ShieldAlert color="#ef4444" /> Backend Agent Failed</h3>
              <p>{report.error}</p>
              <button className="glow-btn" onClick={() => setReport(null)} style={{ marginTop: '16px' }}>Go Back</button>
            </div>
        )}

        {report && report.status === "success" && (
          <div className="results-container">
            <div className="glass-panel" style={{ marginBottom: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <h2>{report.repository}</h2>
                <p style={{ color: 'var(--text-secondary)' }}>Successfully scanned <b>{report.files_scanned}</b> files securely.</p>
              </div>
              <button className="glow-btn" onClick={() => setReport(null)}>New Scan</button>
            </div>

            <h3 style={{ marginBottom: '16px', color: 'var(--text-secondary)', borderBottom: '1px solid var(--border-color)', paddingBottom: '8px' }}>
              Identified Compliance Violations ({report.findings?.llm_compliance?.length || 0})
            </h3>
            
            <div className="results-grid">
              {report.findings?.llm_compliance?.length === 0 && (
                <div className="glass-panel">
                  <p style={{ color: 'var(--text-secondary)' }}>No violations found! Your code meets compliance standards.</p>
                </div>
              )}
              {report.findings?.llm_compliance?.map((finding, idx) => (
                <div key={idx} className={`glass-panel threat-card ${finding.severity.toLowerCase()}`}>
                  <h3>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <Bug size={24} color={finding.severity === "CRITICAL" ? "#ef4444" : "var(--accent-cyan)"} />
                      {finding.vulnerability_type}
                    </span>
                    <span className="badge" style={{
                      backgroundColor: finding.severity === "CRITICAL" ? "rgba(239, 68, 68, 0.2)" : "rgba(0, 240, 255, 0.2)",
                      color: finding.severity === "CRITICAL" ? "#fca5a5" : "#6ee7b7",
                      borderColor: finding.severity === "CRITICAL" ? "rgba(239, 68, 68, 0.3)" : "rgba(0, 240, 255, 0.3)",
                    }}>{finding.severity}</span>
                  </h3>
                  <p style={{ marginTop: '12px', fontSize: '1.1rem', lineHeight: '1.5' }}>
                    {finding.description}
                  </p>
                  <p style={{ marginTop: '16px', color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <Code size={16} /> <em style={{wordBreak: "break-all"}}>{finding.file}</em>
                  </p>
                  {finding.regulatory_mapping && (
                    <span className="compliance-tag">{finding.regulatory_mapping}</span>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
