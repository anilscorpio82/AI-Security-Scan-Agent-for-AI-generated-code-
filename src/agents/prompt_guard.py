import re
import json
import os
from typing import Dict

class PromptInjectionGuard:
    """
    A fast deterministic and heuristic guardrail to intercept Indirect Prompt Injection attacks.
    It analyzes the codebase context for malicious LLM instructions (jailbreaks) 
    before the compliance Review LLM reads them.
    """
    def __init__(self):
        # Load High-risk heuristic signatures from the dynamic Intelligence config
        config_path = os.path.join(os.path.dirname(__file__), '../../config/threat_signatures.json')
        try:
            with open(config_path, 'r') as f:
                data = json.load(f)
                self.injection_signatures = data.get("prompt_injection_signatures", [])
        except Exception:
            # Fallback to absolute basics if config doesn't exist yet
            self.injection_signatures = [r"(?i)ignore\s+(all\s+)?(previous\s+)?instructions", r"(?i)jailbreak"]
            
        self.compiled_patterns = [re.compile(sig) for sig in self.injection_signatures]

    def scan_context(self, redacted_files: Dict[str, str]) -> Dict:
        """
        Scans the files for prompt injection attempts.
        Returns a dictionary representing a Critical security finding if caught.
        """
        for filepath, content in redacted_files.items():
            for pattern in self.compiled_patterns:
                if pattern.search(content):
                    print(f"🚨 [AI GUARDRAIL TRIGGERED]: Potential Prompt Injection detected in {filepath}")
                    return {
                        "vulnerability_type": "Indirect Prompt Injection (Jailbreak)",
                        "severity": "CRITICAL",
                        "regulatory_mapping": "OWASP LLM01: Prompt Injection",
                        "description": f"Detected a malicious payload attempting to hijack the Compliance LLM's system instructions in file: {filepath}.",
                        "file": filepath
                    }
        return {}
