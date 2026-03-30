import os
import sys
import json
from src.core.orchestrator import SecurityOrchestrator
from langchain_core.language_models.fake_chat_models import FakeListChatModel

def run_ci():
    """
    Entrypoint for GitHub Actions CI/CD to scan a pull request safely.
    It reads the mounted GITHUB_WORKSPACE and fails the build if critical issues are found.
    """
    workspace_path = os.environ.get('GITHUB_WORKSPACE', './')
    print(f"::group::Enterprise Zero-Trust Security Scan: {workspace_path}")
    
    # We use a mocked LLM to demonstrate the CI pipeline failing without needing real API keys
    mock_response = '''
    {
      "findings": [
        {
          "vulnerability_type": "Data Privacy Violation",
          "severity": "CRITICAL",
          "regulatory_mapping": "PCI-DSS Req 3.4 / HIPAA Sec. 164.312",
          "description": "Sensitive payment and patient profile data is written to a flat text file without any encryption."
        }
      ]
    }
    '''
    
    mock_patch_response = '''
    {
      "patches": [
        {
          "file": "./tests/vulnerable_repo/bad_healthcare_app.py",
          "unified_diff": "--- bad_healthcare_app.py\\n+++ bad_healthcare_app.py\\n@@ -13,6 +13,6 @@\\n-    with open(\\"billing_logs.txt\\", \\"a\\") as f:\\n-        f.write(cc_log)\\n+    from cryptography.fernet import Fernet\\n+    key = Fernet.generate_key()\\n+    cipher_suite = Fernet(key)\\n+    encrypted_text = cipher_suite.encrypt(cc_log.encode())\\n+    with open(\\"billing_logs.txt\\", \\"ab\\") as f:\\n+        f.write(encrypted_text)",
          "explanation": "Refactored raw PHI file writes to use symmetric AES encryption to satisfy PCI-DSS."
        }
      ]
    }
    '''
    llm = FakeListChatModel(responses=[mock_response, mock_patch_response])
    orchestrator = SecurityOrchestrator(llm_engine=llm)
    
    try:
        report = orchestrator.run(workspace_path)
        print("Detailed Audit Report:")
        print(json.dumps(report, indent=2))
        print("::endgroup::")
        
        # Determine CI/CD status based on findings
        compliance_issues = report.get("findings", {}).get("llm_compliance", [])
        critical_findings = [f for f in compliance_issues if f.get("severity") in ["CRITICAL", "HIGH"]]
        
        if critical_findings:
            print(f"::error::Compliance Review Failed! 🚨 Omni-Analyzer intercepted {len(critical_findings)} HIGH/CRITICAL violations prior to merging.")
            # Fails the GitHub Action build step
            sys.exit(1)
            
        print("✅ Compliance Scan Passed! Zero-trust PII redaction and SAST confirmed no violations.")
        sys.exit(0)
        
    except Exception as e:
        print(f"::error::Omni-Analyzer failed to run: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    run_ci()
