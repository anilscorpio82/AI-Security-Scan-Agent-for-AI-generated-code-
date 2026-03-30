from fastapi import FastAPI, BackgroundTasks, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
import os
import uvicorn
from dotenv import load_dotenv
from typing import Dict, Any, List
from datetime import timedelta

from langchain_core.language_models.fake.chat_models import FakeListChatModel
from src.core.orchestrator import SecurityOrchestrator
from src.api.auth import create_access_token, get_current_active_user, verify_password, ACCESS_TOKEN_EXPIRE_MINUTES, fake_users_db

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

@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = fake_users_db.get(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/scan")
async def start_scan(request: ScanRequest, background_tasks: BackgroundTasks, current_user: dict = Depends(get_current_active_user)):
    """
    Kicks off an asynchronous LangGraph Enterprise audit.
    Requires IAM JWT authorization.
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
