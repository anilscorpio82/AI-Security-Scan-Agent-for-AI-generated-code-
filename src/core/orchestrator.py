from typing import Dict, List, TypedDict, Any
from langgraph.graph import StateGraph, END
import os
import json

from src.core.context_aggregator import ContextAggregator
from src.core.pii_redactor import PIIRedactor
from src.agents.sast_scanner import SASTScanner
from src.agents.compliance_reviewer import ComplianceReviewer
from src.agents.remediation_agent import RemediationAgent
from src.agents.prompt_guard import PromptInjectionGuard

# Define the state for LangGraph workflow
class AgentState(TypedDict):
    repo_path: str
    original_files: Dict[str, str]
    redacted_files: Dict[str, str]
    vector_store: Any
    sast_findings: List[Dict]
    compliance_findings: List[Dict]
    remediation_patches: List[Dict]
    final_report: Dict[str, Any]
    error: str

class SecurityOrchestrator:
    """
    Orchestrates the Enterprise AI Security pipeline using LangGraph:
    Context -> Redact -> SAST -> LLM Review -> [Auto-Remediate] -> Reporting
    """
    def __init__(self, llm_engine=None):
        self.context_aggregator = None
        self.pii_redactor = PIIRedactor()
        self.sast_scanner = SASTScanner()
        
        if llm_engine:
            self.compliance_reviewer = ComplianceReviewer(llm_engine)
            self.remediation_agent = RemediationAgent(llm_engine)
            self.compliance_reviewer = None
            self.remediation_agent = None
            
        self.prompt_guard = PromptInjectionGuard()
        self.graph = self._build_graph()
        
    def _build_graph(self):
        workflow = StateGraph(AgentState)
        
        workflow.add_node("aggregate_context", self.node_aggregate_context)
        workflow.add_node("redact_pii", self.node_redact_pii)
        workflow.add_node("guardrail_scan", self.node_guardrail_scan)
        workflow.add_node("sast_scan", self.node_sast_scan)
        workflow.add_node("build_rag_vectors", self.node_build_vectors)
        workflow.add_node("llm_compliance_review", self.node_llm_review)
        workflow.add_node("auto_remediate", self.node_auto_remediate)
        workflow.add_node("generate_report", self.node_generate_report)
        
        # Pipeline Flow
        workflow.set_entry_point("aggregate_context")
        workflow.add_edge("aggregate_context", "redact_pii")
        workflow.add_edge("redact_pii", "guardrail_scan")
        workflow.add_edge("guardrail_scan", "sast_scan")
        workflow.add_edge("sast_scan", "build_rag_vectors")
        workflow.add_edge("build_rag_vectors", "llm_compliance_review")
        
        # Conditional logic: only remediate if we found flaws
        workflow.add_conditional_edges(
            "llm_compliance_review",
            self.should_remediate,
            {
                "remediate": "auto_remediate",
                "report": "generate_report"
            }
        )
        
        workflow.add_edge("auto_remediate", "generate_report")
        workflow.add_edge("generate_report", END)
        
        return workflow.compile()
        
    def should_remediate(self, state: AgentState) -> str:
        # Check if there are compliance/SAST findings
        all_findings = state.get("sast_findings", []) + state.get("compliance_findings", [])
        has_criticals = any(f.get("severity") in ["CRITICAL", "HIGH"] for f in all_findings)
        
        if has_criticals and self.remediation_agent:
            return "remediate"
        return "report"
        
    def node_aggregate_context(self, state: AgentState):
        aggregator = ContextAggregator(state['repo_path'])
        files = aggregator.extract_context()
        if not files:
            return {"error": "No valid source files found in repo."}
        return {"original_files": files}

    def node_redact_pii(self, state: AgentState):
        if state.get("error"): return state
        redacted_files = {}
        for path, content in state["original_files"].items():
            redacted_files[path] = self.pii_redactor.redact_code(content)
        return {"redacted_files": redacted_files}
        
    def node_guardrail_scan(self, state: AgentState):
        if state.get("error"): return state
        injection_finding = self.prompt_guard.scan_context(state["redacted_files"])
        findings = state.get("sast_findings", [])
        if injection_finding:
            findings.append(injection_finding)
        return {"sast_findings": findings}
        
    def node_sast_scan(self, state: AgentState):
        if state.get("error"): return state
        findings = state.get("sast_findings", [])
        findings.extend(self.sast_scanner.scan(state["redacted_files"]))
        return {"sast_findings": findings}
        
    def node_build_vectors(self, state: AgentState):
        if state.get("error") or not state.get("redacted_files"):
            return state
        aggregator = ContextAggregator(state['repo_path'])
        vector_store = aggregator.build_vector_store(state['redacted_files'])
        return {"vector_store": vector_store}
        
    def node_llm_review(self, state: AgentState):
        if state.get("error") or not self.compliance_reviewer: 
            return {"compliance_findings": []}
        findings = self.compliance_reviewer.review_code_batch(
            state["redacted_files"],
            vector_store=state.get("vector_store")
        )
        return {"compliance_findings": findings}
        
    def node_auto_remediate(self, state: AgentState):
        if state.get("error") or not self.remediation_agent:
            return {"remediation_patches": []}
        
        findings = state.get("compliance_findings", []) + state.get("sast_findings", [])
        patches = self.remediation_agent.generate_patches(state["original_files"], findings)
        return {"remediation_patches": patches}
        
    def node_generate_report(self, state: AgentState):
        if state.get("error"):
            return {"final_report": {"status": "failed", "error": state["error"]}}
            
        report = {
            "status": "success",
            "repository": state["repo_path"],
            "files_scanned": len(state["redacted_files"]),
            "findings": {
                "sast_deterministic": state.get("sast_findings", []),
                "llm_compliance": state.get("compliance_findings", [])
            },
            "remediation": state.get("remediation_patches", [])
        }
        return {"final_report": report}
        
    def run(self, repo_path: str):
        initial_state = {
            "repo_path": repo_path,
            "original_files": {},
            "redacted_files": {},
            "vector_store": None,
            "sast_findings": [],
            "compliance_findings": [],
            "remediation_patches": [],
            "final_report": {},
            "error": ""
        }
        print(f"Starting Enterprise Security Scan on: {repo_path}")
        final_state = self.graph.invoke(initial_state)
        return final_state.get("final_report", {})
