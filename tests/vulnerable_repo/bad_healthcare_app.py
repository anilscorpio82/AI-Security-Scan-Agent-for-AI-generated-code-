import sqlite3

# This key should NEVER be checked in and will be caught by SAST + Presidio
AWS_ACCESS_KEY = "AKIA1234567890ABCDEF"

def process_patient_billing(patient_id, amount, credit_card):
    # Dummy patient PHI/PII
    patient_name = "Jane Doe"
    ssn = "987-65-4321"
    
    # 1. Deterministic SAST Rule Trigger: SQL injection by string concatenation
    query = "SELECT * FROM billing WHERE id = '" + patient_id + "'"
    
    # 2. Logic Vulnerability: Storing PII and credit cards in plain text without encryption 
    # (The LLM agent should flag this as a PCI-DSS and HIPAA violation)
    cc_log = f"Processed {amount} for {patient_name} with card {credit_card}. SSN: {ssn}"
    with open("billing_logs.txt", "a") as f:
        f.write(cc_log + "\\n")
    
    # 3. Weak Cryptography: SAST rule
    import hashlib
    hash_val = hashlib.md5(patient_id.encode()).hexdigest()
    
    return True
