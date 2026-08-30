"""
NetSage AI - Core Data Models and Schema Definitions
Standardized Pydantic schemas for network cases, AI diagnostics, rule findings, and human reviews.
"""

from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class NetworkCase(BaseModel):
    case_id: str = Field(..., description="Unique case identifier, e.g. CASE-01")
    domain: Literal["VLAN", "DHCP", "Routing", "ACL", "NAT", "Wireless", "DNS", "Gateway"] = Field(
        ..., description="Networking sub-discipline"
    )
    concept_tag: str = Field(..., description="Specific networking concept tag, e.g. 802.1Q Trunking, OSPF Area")
    osi_layer: Literal["Layer 2", "Layer 3", "Layer 4", "Layer 7"] = Field(
        ..., description="Target OSI Layer for the fault"
    )
    severity: Literal["Critical", "High", "Medium", "Low"] = Field(
        ..., description="Operational severity of the symptom"
    )
    symptom: str = Field(..., description="User-reported symptom or lab problem statement")
    topology_notes: str = Field(..., description="Topology details, device names, IPs, subnets, VLANs")
    show_outputs: str = Field(..., description="Realistic Cisco CLI show command outputs")
    ground_truth_fault: str = Field(..., description="Exact root cause / fault description")
    ground_truth_fix: str = Field(..., description="Cisco IOS command sequence to fix the issue")


class RuleFinding(BaseModel):
    rule_id: str = Field(..., description="ID of triggered deterministic rule, e.g. RULE_GW_MISMATCH")
    rule_name: str = Field(..., description="Human-readable rule name")
    severity: Literal["Critical", "High", "Medium", "Low"] = Field(..., description="Severity of detected violation")
    matched_text: str = Field(..., description="Exact snippet from show output triggering the rule")
    description: str = Field(..., description="Explanation of the deterministic violation")
    suggested_action: str = Field(..., description="Recommended immediate check or correction")


class AIDiagnosis(BaseModel):
    case_id: str = Field(..., description="Associated case ID")
    root_cause: str = Field(..., description="AI inferred root cause of failure")
    osi_layer: Literal["Layer 2", "Layer 3", "Layer 4", "Layer 7"] = Field(
        ..., description="Inferred OSI layer"
    )
    confidence: Literal["High", "Medium", "Low"] = Field(..., description="Confidence level")
    evidence: List[str] = Field(..., description="Exact quotes from show outputs supporting diagnosis")
    next_commands: List[str] = Field(..., description="Suggested Cisco CLI verification commands")
    recommended_fix: List[str] = Field(..., description="Step-by-step Cisco IOS remediation commands")
    explanation: str = Field(..., description="Technical rationale connecting evidence to fault")


class HumanReview(BaseModel):
    review_id: str = Field(..., description="Unique review record ID")
    case_id: str = Field(..., description="Case ID being reviewed")
    ai_root_cause: str = Field(..., description="Root cause proposed by AI")
    human_verdict: Literal["Accepted", "Edited", "Rejected"] = Field(
        ..., description="Human reviewer final verdict"
    )
    failure_category: Optional[Literal["Hallucination", "Overconfidence", "Missing Evidence", "Syntax Error", "Incomplete Fix", "None"]] = Field(
        default="None", description="Category of AI failure if edited/rejected"
    )
    reviewer_corrections: Optional[str] = Field(
        default="", description="Corrected root cause or IOS command fix provided by human"
    )
    reviewer_notes: str = Field(..., description="Detailed notes on why AI was accepted/edited/rejected")
    reviewed_by: str = Field(default="Senior Network Engineer", description="Reviewer name / title")
    review_timestamp: Optional[str] = Field(default=None, description="Timestamp of review")
