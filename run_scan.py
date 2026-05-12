from dotenv import load_dotenv
import json
import os
import asyncio

load_dotenv()

def build_llm():
    """
    Auto-detects the available LLM provider from environment variables.
    Priority: ANTHROPIC_API_KEY → GOOGLE_API_KEY → FakeListChatModel (staging)
    """
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    google_key    = os.getenv("GOOGLE_API_KEY")

    if anthropic_key:
        from langchain_anthropic import ChatAnthropic
        model = os.getenv("CLAUDE_MODEL", "claude-3-5-haiku-20241022")
        print(f"🤖 LLM Provider: Anthropic Claude ({model})")
        return ChatAnthropic(
            model=model,
            api_key=anthropic_key,
            temperature=0,
            max_tokens=4096,
        )

    if google_key:
        from langchain_google_genai import ChatGoogleGenerativeAI
        model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        print(f"🤖 LLM Provider: Google Gemini ({model})")
        return ChatGoogleGenerativeAI(
            model=model,
            google_api_key=google_key,
            temperature=0,
        )

    # ── Staging fallback: deterministic mock so scan runs without any API key ──
    from langchain_core.language_models.fake_chat_models import FakeListChatModel
    print("⚠️  No API key found — using FakeListChatModel (staging/demo mode)")
    print("   Set ANTHROPIC_API_KEY or GOOGLE_API_KEY in your .env to enable real LLM analysis.\n")

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
          "unified_diff": "--- bad_healthcare_app.py\\n+++ bad_healthcare_app.py\\n@@ -13,6 +13,6 @@\\n-    with open(\\\"billing_logs.txt\\\", \\\"a\\\") as f:\\n-        f.write(cc_log)\\n+    from cryptography.fernet import Fernet\\n+    key = Fernet.generate_key()\\n+    cipher = Fernet(key)\\n+    encrypted_log = cipher.encrypt(cc_log.encode())\\n+    with open(\\\"billing_logs.txt\\\", \\\"ab\\\") as f:\\n+        f.write(encrypted_log)",
          "explanation": "Added Fernet encryption to sanitize PCI/PHI local storage."
        }
      ]
    }
    '''
    return FakeListChatModel(responses=[mock_response, mock_patch_response])


async def main():
    from src.core.orchestrator import SecurityOrchestrator

    llm = build_llm()
    orchestrator = SecurityOrchestrator(llm_engine=llm)

    repo_to_scan = os.getenv("SCAN_TARGET", "./tests/vulnerable_repo/")
    print(f"🔍 Scanning Repository: {repo_to_scan}\n")

    report = orchestrator.run(repo_to_scan)

    print("\n================ FINAL SECURITY REPORT ================")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
