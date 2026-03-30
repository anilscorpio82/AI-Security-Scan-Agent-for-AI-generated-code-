from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern
from presidio_anonymizer import AnonymizerEngine

class PIIRedactor:
    def __init__(self):
        # We initialize the presidio engines. 
        self.analyzer = AnalyzerEngine()
        self.anonymizer = AnonymizerEngine()
        
        # Add custom recognizer for API Keys or proprietary tokens (e.g. AWS Keys)
        aws_key_pattern = Pattern(name="aws_key", regex="AKIA[0-9A-Z]{16}", score=0.9)
        aws_recognizer = PatternRecognizer(supported_entity="AWS_API_KEY", patterns=[aws_key_pattern])
        self.analyzer.registry.add_recognizer(aws_recognizer)
        
    def redact_code(self, source_code: str) -> str:
        """
        Takes raw source code and redacts sensitive PII/PHI information
        (e.g., medical numbers, names, credit cards, emails, api keys) 
        before sending it to any LLM.
        """
        # Empty entities list means all supported default entities are matched
        results = self.analyzer.analyze(text=source_code, entities=[], language='en')
        
        # Redact the findings
        anonymized = self.anonymizer.anonymize(text=source_code, analyzer_results=results)
        
        return anonymized.text

# Test block if executed directly
if __name__ == "__main__":
    redactor = PIIRedactor()
    sample_code = """
def process_patient_data():
    patient_name = "John Doe"
    ssn = "123-45-6789"
    email = "john.doe@hospital.org"
    aws_key = "AKIA1234567890ABCDEF"
    # Log patient access
    print(f"Accessed records for {patient_name} with email {email}")
    return True
"""
    redacted = redactor.redact_code(sample_code)
    print("Original Code:")
    print(sample_code)
    print("---------------------------------")
    print("Redacted Safe Code:")
    print(redacted)
