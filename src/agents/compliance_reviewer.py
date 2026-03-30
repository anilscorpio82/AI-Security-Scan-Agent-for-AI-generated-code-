import json
from pydantic import BaseModel, Field
from typing import List

class ComplianceFinding(BaseModel):
    vulnerability_type: str = Field(description="The type of logical vulnerability found (e.g. Broken Access Control).")
    severity: str = Field(description="Severity measure: CRITICAL, HIGH, MEDIUM, LOW.")
    regulatory_mapping: str = Field(description="The exact regulatory framework violation (e.g., HIPAA Sec. 164.312, PCI-DSS Req 3).")
    description: str = Field(description="Detailed explanation of the issue.")

class CodeReviewOutput(BaseModel):
    findings: List[ComplianceFinding] = Field(description="A list of compliance violation findings.")

class ComplianceReviewer:
    """
    Simulates the deep LLM review of the sanitized source code.
    It focuses on business logic flaws and AI hallucinations that SAST misses,
    mapping everything to Enterprise Compliance standards.
    """
    def __init__(self, llm_engine):
        # We expect a LangChain Chat Model (e.g. ChatOpenAI, ChatOllama, ChatGoogleGenerativeAI)
        from langchain_core.output_parsers import PydanticOutputParser
        from langchain_core.prompts import PromptTemplate

        self.llm = llm_engine
        self.parser = PydanticOutputParser(pydantic_object=CodeReviewOutput)
        self.prompt = PromptTemplate(
            template="You are an expert Enterprise Security and Compliance AI Agent. "
                     "Review the following source code for business logic flaws, "
                     "data privacy violations, and security anti-patterns.\n"
                     "Focus particularly on PII/PHI data handling, encryption, and authorization.\n"
                     "Return the results mapped to PCI-DSS, HIPAA, or SOC 2 where applicable.\n\n"
                     "Code Content to Review:\n{code_content}\n\n"
                     "{format_instructions}",
            input_variables=["code_content"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )
        self.chain = self.prompt | self.llm | self.parser

    def review_code_batch(self, files_context: dict) -> List[dict]:
        """
        Reviews chunks of code. In an enterprise system, this would be highly parallelized
        or split into syntax trees.
        """
        all_findings = []
        for file_path, content in files_context.items():
            # Basic chunking simulation
            if not content.strip():
                continue
            
            try:
                result: CodeReviewOutput = self.chain.invoke({"code_content": content})
                
                # Append file path context to each finding
                for finding in result.findings:
                    finding_dict = finding.model_dump()
                    finding_dict['file'] = file_path
                    all_findings.append(finding_dict)
            except Exception as e:
                print(f"Error during LLM review of {file_path}: {e}")
                
        return all_findings
