# Google Antigravity Developer Integration Guide

**Subject:** Native MCP (Model Context Protocol) Hook setup for Omni-Analyzer

---

## 🚀 The Paradigm Shift
You no longer need to upload your codebase to the web dashboard to check for compliance bugs! The Omni-Analyzer has been built as a native **MCP Server**. This means your local IDE AI (Google Antigravity) can seamlessly forward your code through the Zero-Trust Presidio & LangGraph compliance gateway natively.

When you ask Antigravity, *"Are there any security issues in my current file?"* it will automatically trigger the `audit_enterprise_codebase` MCP tool. 

If vulnerabilities are detected, Antigravity will print the actual `.patch` fixes back into your chat screen so you can immediately "Accept Fix"!

## 🔧 Prerequisites
Ensure you have cloned this repository locally and installed the virtual environment:
```bash
git clone https://github.com/anilscorpio82/AI-Security-Scan-Agent-for-AI-generated-code-.git
cd AI-Security-Scan-Agent-for-AI-generated-code-
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install mcp
```

## 🔌 Connecting Google Antigravity
Google Antigravity uses standard JSON configuration to mount external tools.

1. Locate your Antigravity (or Cline) MCP settings file natively.
2. Inject the following JSON block:

```json
{
  "mcpServers": {
    "omni-analyzer-security": {
      "command": "/absolute/path/to/AI-Security-Scan-Agent-for-AI-generated-code-/venv/bin/python",
      "args": [
        "/absolute/path/to/AI-Security-Scan-Agent-for-AI-generated-code-/src/api/mcp_server.py"
      ],
      "env": {
         "GOOGLE_API_KEY": "YOUR-ENTERPRISE-DEVELOPER-KEY"
      }
    }
  }
}
```

### 💡 Validation
Restart your Antigravity extension. You should now see `audit_enterprise_codebase` listed under your "Available Tools". 

You can literally tell your AI:
> *"Audit my `backend/` folder via the Omni-Analyzer. If it finds anything, apply the patch files automatically."*
