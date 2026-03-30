from dotenv import load_dotenv
import json
import asyncio
from langchain_core.language_models.fake_chat_models import FakeListChatModel
from src.core.orchestrator import SecurityOrchestrator

load_dotenv()

async def main():
    # Mock LLM response to simulate the Compliance Reviewer output since we don't have API keys in the staging environment
    mock_response = '''
    {
      "findings": [
        {
          "vulnerability_type": "Data Privacy Violation",
          "severity": "CRITICAL",
          "regulatory_mapping": "PCI-DSS Req 3.4 / HIPAA Sec. 164.312",
          "description": "Sensitive payment and patient profile data is written to a flat text file (billing_logs.txt) without any encryption."
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
          "explanation": "Added Fernet encryption to sanitize PCI/PHI local storage."
        }
      ]
    }
    '''
    
    # Using FakeListChatModel to simulate an Enterprise LLM API call
    llm = FakeListChatModel(responses=[mock_response, mock_patch_response])
    orchestrator = SecurityOrchestrator(llm_engine=llm)
    
    repo_to_scan = "./tests/vulnerable_repo/"
    print(f"Scanning Repository: {repo_to_scan}\\n")
    
    report = orchestrator.run(repo_to_scan)
    
    print("================ FINAL SECURITY REPORT ================")
    print(json.dumps(report, indent=2))
    
if __name__ == "__main__":
    asyncio.run(main())
