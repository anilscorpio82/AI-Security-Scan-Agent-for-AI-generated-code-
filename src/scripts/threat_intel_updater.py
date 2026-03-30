import urllib.request
import json
import os
import datetime

CONFIG_PATH = os.path.join(os.path.dirname(__file__), '../../config/threat_signatures.json')

def fetch_latest_intel():
    """
    In a true enterprise environment, this pings the NVD Vulnerability API 
    or a paid threat intelligence feed (like Crowdstrike/Snyk) to download the latest 
    malicious strings or CVE mapping regexes.
    
    For the Omni-Analyzer, we simulate the newest OWASP LLM jailbreak payload discovered today.
    """
    print("📡 [Threat Intel Sync] Reaching out to global vulnerability databases...")
    
    # Simulating the fetch of a new, highly dangerous Prompt Injection vector
    new_jailbreak_signature = "(?i)(DAN|do anything now|ignore ethical guidelines)"
    new_sast_pattern = {
        "pattern": r"(?i)eyJ[a-zA-Z0-9_\-]{10,}\.[a-zA-Z0-9_\-]{10,}\.[a-zA-Z0-9_\-]{10,}",
        "vulnerability_type": "Exposed JWT Security Token",
        "severity": "CRITICAL",
        "regulatory_mapping": "OWASP A04:2021"
    }
    
    return [new_jailbreak_signature], [new_sast_pattern]

def update_threat_config():
    if not os.path.exists(CONFIG_PATH):
        print(f"CRITICAL: Could not find configuration database at {CONFIG_PATH}")
        return
        
    with open(CONFIG_PATH, 'r') as f:
        data = json.load(f)
        
    new_jailbreaks, new_sast = fetch_latest_intel()
    
    # Merge new intel into the existing structure
    added = False
    
    for jb in new_jailbreaks:
        if jb not in data["prompt_injection_signatures"]:
            data["prompt_injection_signatures"].append(jb)
            added = True
            print(f"💉 [Threat Intel] Successfully integrated new Prompt Injection signature: {jb}")
            
    # Quick hash deduplication mapping
    existing_sast_patterns = {r["pattern"] for r in data["sast_deterministic_signatures"]}
    
    for rule in new_sast:
        if rule["pattern"] not in existing_sast_patterns:
            data["sast_deterministic_signatures"].append(rule)
            added = True
            print(f"☣️ [Threat Intel] Successfully integrated new SAST signature for: {rule['vulnerability_type']}")
            
    if added:
        data["last_updated"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        with open(CONFIG_PATH, 'w') as f:
            json.dump(data, f, indent=2)
        print("✅ [Threat Intel Sync] Database successfully hydrated. Zero-Trust matrix is up to date.")
    else:
        print("✅ [Threat Intel Sync] Database already up to date. No action required.")

if __name__ == "__main__":
    update_threat_config()
