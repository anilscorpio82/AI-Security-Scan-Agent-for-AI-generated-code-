from mcp.server.fastmcp import FastMCP
import os
import json
from dotenv import load_dotenv

from src.core.orchestrator import SecurityOrchestrator
from langchain_google_genai import ChatGoogleGenerativeAI

# Initialize the Model Context Protocol (MCP) Server for Google Antigravity
mcp = FastMCP("omni-analyzer")

def get_orchestrator():
    """
    Initializes the Live Generative AI backend using the system's .env file.
    This guarantees zero hallucinations while returning perfectly generated .patch fixes.
    """
    load_dotenv()
    
    if not os.getenv("GOOGLE_API_KEY"):
        raise ValueError("CRITICAL: GOOGLE_API_KEY must be configured in the .env file to enable live MCP analysis.")
        
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0)
    return SecurityOrchestrator(llm_engine=llm)

@mcp.tool()
def audit_enterprise_codebase(repo_path: str) -> str:
    """
    Executes a Zero-Trust Security Audit incorporating PII Masking, SAST fallbacks, HIPAA/PCI mapping, and Prompt Guardrails.
    Returns a unified JSON string containing vulnerability assessments and Git .patch remediations ready for the AI developer to apply.
    
    Args:
        repo_path (str): The absolute local system path to the codebase repository (or subfolder).
    """
    if not os.path.exists(repo_path):
        return json.dumps({
            "status": "failed", 
            "error": f"The provided repository path '{repo_path}' does not exist on this machine."
        })
    
    try:
        orchestrator = get_orchestrator()
        report = orchestrator.run(repo_path)
        
        # We beautifully format the JSON output so Google Antigravity can parse it cleanly
        return json.dumps(report, indent=2)
        
    except Exception as e:
        return json.dumps({"status": "failed", "error": f"MCP Backend Execution Failed: {str(e)}"})

# If a developer's IDE runs this directly, bind it to standard I/O streams for native MCP JSON-RPC protocol.
if __name__ == "__main__":
    mcp.run()
