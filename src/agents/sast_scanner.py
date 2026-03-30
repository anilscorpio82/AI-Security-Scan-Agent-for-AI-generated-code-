import os
import json
import re
from typing import Dict, List

class SASTScanner:
    """
    Acts as a wrapper for deterministic Enterprise SAST tools (e.g. Semgrep, Gitleaks, Checkmarx).
    In this PoC, it mocks findings by looking for simplistic patterns that represent
    what an actual tool would detect.
    """
    def __init__(self):
        # Load SAST signatures from the dynamically updated configuration database
        config_path = os.path.join(os.path.dirname(__file__), '../../config/threat_signatures.json')
        try:
            with open(config_path, 'r') as f:
                data = json.load(f)
                self.known_bad_patterns = data.get("sast_deterministic_signatures", [])
        except Exception:
            self.known_bad_patterns = []
            
        self.compiled_rules = []
        for rule in self.known_bad_patterns:
            try:
                self.compiled_rules.append({
                    "pattern": re.compile(rule["pattern"]),
                    "vulnerability_type": rule["vulnerability_type"],
                    "severity": rule["severity"],
                    "description": rule.get("regulatory_mapping", "Deterministic AST/Regex rule.")
                })
            except Exception:
                continue

    def scan(self, files_context: Dict[str, str]) -> List[Dict]:
        """
        Scans all collected code files against deterministic SAST rules.
        """
        findings = []
        for file_path, content in files_context.items():
            for rule in self.compiled_rules:
                if rule["pattern"].search(content):
                    findings.append({
                        "file": file_path,
                        "vulnerability_type": rule["vulnerability_type"],
                        "severity": rule["severity"],
                        "description": rule["description"]
                    })
        return findings
