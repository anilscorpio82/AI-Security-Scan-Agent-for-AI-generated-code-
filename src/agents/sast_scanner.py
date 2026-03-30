from typing import Dict, List

class SASTScanner:
    """
    Acts as a wrapper for deterministic Enterprise SAST tools (e.g. Semgrep, Gitleaks, Checkmarx).
    In this PoC, it mocks findings by looking for simplistic patterns that represent
    what an actual tool would detect.
    """
    def __init__(self):
        # A mock set of known deterministic bad patterns (regex/AST simulations)
        self.known_bad_patterns = [
            # Hardcoded secret mockup
            {"pattern": "AKIA", "severity": "CRITICAL", "type": "Hardcoded Secret", "desc": "AWS API Key detected in code."},
            # SQL Injection mockup
            {"pattern": "SELECT * FROM users WHERE username = '\" +", "severity": "HIGH", "type": "SQL Injection", "desc": "String concatenation in SQL query."},
            # Weak hashing mockup
            {"pattern": "md5(", "severity": "MEDIUM", "type": "Weak Cryptography", "desc": "MD5 is insecure for hashing data."}
        ]

    def scan(self, files_context: Dict[str, str]) -> List[Dict]:
        """
        Scans all collected code files against deterministic SAST rules.
        """
        findings = []
        for file_path, content in files_context.items():
            for rule in self.known_bad_patterns:
                if rule["pattern"] in content:
                    findings.append({
                        "file": file_path,
                        "vulnerability_type": rule["type"],
                        "severity": rule["severity"],
                        "description": rule["desc"]
                    })
        return findings
