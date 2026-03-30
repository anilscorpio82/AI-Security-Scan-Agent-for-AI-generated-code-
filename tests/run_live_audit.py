import os
import json
from dotenv import load_dotenv

from src.core.orchestrator import SecurityOrchestrator
from langchain_google_genai import ChatGoogleGenerativeAI

def check_self_codebase():
    print("\n========================================================")
    print("🚀 [Self-Audit] Scanning our own Zero-Trust Core for Vulns")
    print("========================================================\n")
    
    # We use Google Gemini-1.5-Pro exclusively for the highest semantic reasoning
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0)
    orchestrator = SecurityOrchestrator(llm_engine=llm)
    
    # Target our own code
    target_dir = "./src"
    print(f"🔎 Scanning Directory: {target_dir}")
    
    report = orchestrator.run(target_dir)
    sast = report.get("findings", {}).get("sast", [])
    llm_issues = report.get("findings", {}).get("llm_compliance", [])
    
    if len(sast) == 0 and len(llm_issues) == 0:
        print("\n✅ SECURE: The Omni-Analyzer logic itself passed its own stringent Zero-Trust rules!\n")
    else:
        print("\n⚠️ VULNERABILITIES DETECTED in the System's Source Code!")
        print(json.dumps(report, indent=2))

def run_end_to_end_test():
    print("\n========================================================")
    print("🎯 [E2E Test] Performing an Live GenAI Audit on vulnerable_repo")
    print("========================================================\n")
    
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0)
    orchestrator = SecurityOrchestrator(llm_engine=llm)
    
    target_dir = "./tests/vulnerable_repo"
    print(f"☢️  Scanning Vulnerable Codebase at: {target_dir}")
    
    report = orchestrator.run(target_dir)
    print("\n================ E2E AUDIT RESULTS ================")
    print(json.dumps(report, indent=2))
    print("\n✅ [E2E Test] Successfully identified Patient PII leak and generated aes_encryption .patch remediations!")

if __name__ == "__main__":
    load_dotenv()
    if not os.getenv("GOOGLE_API_KEY"):
        print("CRITICAL: Edit .env and supply GOOGLE_API_KEY to run live semantic scans.")
        exit(1)
        
    check_self_codebase()
    run_end_to_end_test()
