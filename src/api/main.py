from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import uvicorn
from dotenv import load_dotenv

from langchain_core.language_models import FakeListChatModel
from src.core.orchestrator import SecurityOrchestrator

load_dotenv()

app = FastAPI(
    title="Enterprise AI Security API", 
    description="Zero-Trust AI Agent Security Scanner with PII Redaction and PCI-DSS Mapping."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ScanRequest(BaseModel):
    repo_path: str

# Used Mock LLM so API can be hit locally without API keys
mock_response = '''
{
  "findings": [
    {
      "vulnerability_type": "Data Privacy Violation",
      "severity": "CRITICAL",
      "regulatory_mapping": "PCI-DSS Req 3.4 / HIPAA Sec. 164.312",
      "description": "Sensitive payment and patient profile data is written to a flat text file without any encryption.",
      "file": "./tests/vulnerable_repo/bad_healthcare_app.py"
    }
  ]
}
'''
mock_patch_response = '''
{
  "patches": [
    {
      "file": "./tests/vulnerable_repo/bad_healthcare_app.py",
      "unified_diff": "--- bad_healthcare_app.py\\n+++ bad_healthcare_app.py\\n@@ -13,6 +13,6 @@\\n-    with open(\\"billing_logs.txt\\", \\"a\\") as f:\\n-        f.write(cc_log)\\n+    from cryptography.fernet import Fernet\\n+    key = Fernet.generate_key()\\n+    cipher = Fernet(key)\\n+    encrypted_log = cipher.encrypt(cc_log.encode())\\n+    with open(\\"billing_logs.txt\\", \\"ab\\") as f:\\n+        f.write(encrypted_log)",
      "explanation": "Added symmetric encryption to the file write operation to resolve PHI/PCI leakage."
    }
  ]
}
'''
llm = FakeListChatModel(responses=[mock_response, mock_patch_response])

# Keep orchestrator in memory to avoid re-initializing Presidio models every request
orchestrator = SecurityOrchestrator(llm_engine=llm)

@app.post("/scan/repo")
def scan_repository(request: ScanRequest):
    """
    Triggers the Multi-Agent LLM & SAST pipeline on a given directory.
    """
    if not os.path.exists(request.repo_path):
        raise HTTPException(status_code=400, detail=f"Repository path '{request.repo_path}' does not exist.")
        
    try:
        report = orchestrator.run(request.repo_path)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "Enterprise AI Security Agent is running securely."}

if __name__ == "__main__":
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True)
