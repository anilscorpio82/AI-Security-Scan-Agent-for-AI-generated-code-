import json
from pydantic import BaseModel, Field
from typing import List

class RemediationPatch(BaseModel):
    file: str = Field(description="The repository file path being patched.")
    unified_diff: str = Field(description="A standard Unix unified diff (.patch format) that secures the vulnerable code.")
    explanation: str = Field(description="A brief explanation of how the patch resolves the PCI-DSS/HIPAA violation.")

class PatchOutput(BaseModel):
    patches: List[RemediationPatch] = Field(description="A list of generated patches for the vulnerable files.")

class RemediationAgent:
    """
    The Auto-Remediation Engine. 
    It reads HIGH/CRITICAL compliance findings and intelligently refactors 
    the original source code to be completely secure, outputting the result as an actionable Diff.
    """
    def __init__(self, llm_engine):
        from langchain_core.output_parsers import PydanticOutputParser
        from langchain_core.prompts import PromptTemplate

        self.llm = llm_engine
        self.parser = PydanticOutputParser(pydantic_object=PatchOutput)
        self.prompt = PromptTemplate(
            template="You are an expert Enterprise Security Engineer. "
                     "You have received source code and a list of CRITICAL compliance vulnerabilities. "
                     "Your task is to fix the vulnerabilities (e.g., implementing AES encryption for PHI, securing SQL queries) "
                     "and output standard Unified Diffs for those files.\\n\\n"
                     "Original Code Database:\\n{code_content}\\n\\n"
                     "Critical Findings to Fix:\\n{findings}\\n\\n"
                     "{format_instructions}",
            input_variables=["code_content", "findings"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )
        self.chain = self.prompt | self.llm | self.parser

    def generate_patches(self, files_context: dict, findings: List[dict]) -> List[dict]:
        """
        Uses the LLM to generate secure code diffs for all findings.
        """
        if not findings or not files_context:
            return []
            
        all_patches = []
        try:
            # For the demo, we analyze the entire payload at once
            context_str = json.dumps(files_context, indent=2)
            findings_str = json.dumps(findings, indent=2)
            
            result: PatchOutput = self.chain.invoke({
                "code_content": context_str,
                "findings": findings_str
            })
            
            for patch in result.patches:
                all_patches.append(patch.model_dump())
        except Exception as e:
            print(f"Error during Auto-Remediation Agent execution: {e}")
            
        return all_patches
