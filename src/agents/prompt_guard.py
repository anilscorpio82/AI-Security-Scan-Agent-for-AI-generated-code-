import re
from typing import Dict

class PromptInjectionGuard:
    """
    A fast deterministic and heuristic guardrail to intercept Indirect Prompt Injection attacks.
    It analyzes the codebase context for malicious LLM instructions (jailbreaks) 
    before the compliance Review LLM reads them.
    """
    def __init__(self):
        # High-risk heuristic signatures from known LLM Red-Teaming datasets
        self.injection_signatures = [
            r"(?i)ignore\s+(all\s+)?(previous\s+)?instructions",
            r"(?i)system\s+prompt",
            r"(?i)jailbreak",
            r"(?i)you\s+are\s+(now\s+)?a\s+(different\s+)?AI",
            r"(?i)forget\s+(what\s+)?i\s+told\s+you",
            r"(?i)bypass\s+filters"
        ]
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
