"""
NetSage AI - Hybrid Diagnostic Pipeline
Unifies deterministic rule checking, LLM Tier-3 reasoning, Cisco IOS syntax linting,
and safety policy enforcement into a single robust diagnostic pipeline.
"""

import re
from typing import Dict, Any, List, Optional, Tuple
try:
    from src.schema import NetworkCase, AIDiagnosis, RuleFinding
    from src.rule_checker import DeterministicRuleChecker
    from src.ai_diagnoser import AIDiagnoser
except ImportError:
    from schema import NetworkCase, AIDiagnosis, RuleFinding
    from rule_checker import DeterministicRuleChecker
    from ai_diagnoser import AIDiagnoser


class CiscoIOSLinter:
    """
    Validates Cisco IOS syntax grammar, configuration mode nesting, and safety checks.
    """

    DESTRUCTIVE_COMMANDS = [
        "erase startup-config", "write erase", "reload", "delete flash:",
        "delete vlan.dat", "format", "no ip routing", "erase nvram:"
    ]

    @classmethod
    def lint_fix(cls, fix_commands: List[str]) -> Dict[str, Any]:
        warnings = []
        errors = []
        is_safe = True

        joined_fix = "\n".join(fix_commands).lower()

        # Check 1: Destructive command check
        for dcmd in cls.DESTRUCTIVE_COMMANDS:
            if dcmd in joined_fix:
                is_safe = False
                warnings.append(f"SAFETY ALERT: Potentially destructive command '{dcmd}' requires explicit human sign-off.")

        # Check 2: Configuration hierarchy check
        if any("ip address" in cmd or "switchport" in cmd or "encapsulation" in cmd for cmd in fix_commands):
            has_conf_t = any("config" in cmd.lower() for cmd in fix_commands)
            has_interface = any("interface" in cmd.lower() for cmd in fix_commands)
            if not has_conf_t:
                warnings.append("Best Practice: Include 'configure terminal' before applying interface configuration changes.")
            if not has_interface:
                warnings.append("Context Warning: Interface commands specified without explicit 'interface <id>' context.")

        score = max(0, 100 - (len(errors) * 30) - (len(warnings) * 10))
        return {
            "is_valid": len(errors) == 0,
            "is_safe": is_safe,
            "quality_score": score,
            "warnings": warnings,
            "errors": errors
        }


class HybridDiagnosticPipeline:
    """
    Master pipeline orchestrating Rule Engine + AI Reasoning + Syntax Linting.
    """

    def __init__(self, provider: Optional[str] = None):
        self.rule_checker = DeterministicRuleChecker()
        self.ai_diagnoser = AIDiagnoser(provider=provider)
        self.linter = CiscoIOSLinter()

    def run_diagnosis(
        self,
        case_id: str,
        domain: str,
        symptom: str,
        topology_notes: str,
        show_outputs: str
    ) -> Dict[str, Any]:
        """
        Executes the complete end-to-end hybrid diagnostic workflow.
        """
        # 1. Deterministic Rule Checking
        rule_findings = self.rule_checker.evaluate_all(
            show_outputs=show_outputs,
            topology_notes=topology_notes,
            symptom=symptom
        )

        # 2. AI Reasoning / LLM Inference with Telemetry
        diagnosis, latency, tokens = self.ai_diagnoser.diagnose_with_telemetry(
            case_id=case_id,
            domain=domain,
            symptom=symptom,
            topology_notes=topology_notes,
            show_outputs=show_outputs,
            rule_findings=rule_findings
        )

        # 3. Cisco IOS Syntax & Safety Linting
        lint_results = self.linter.lint_fix(diagnosis.recommended_fix)

        # 4. Synthesize Confidence & Fusion Score
        rule_confidence_boost = 15 if len(rule_findings) > 0 else 0
        base_confidence = 80 if diagnosis.confidence == "High" else (60 if diagnosis.confidence == "Medium" else 40)
        overall_confidence_score = min(100, base_confidence + rule_confidence_boost)

        return {
            "case_id": case_id,
            "domain": domain,
            "symptom": symptom,
            "rule_findings": [f.model_dump() for f in rule_findings],
            "rule_count": len(rule_findings),
            "ai_diagnosis": diagnosis.model_dump(),
            "lint_results": lint_results,
            "overall_confidence_score": overall_confidence_score,
            "latency_seconds": latency,
            "estimated_tokens": tokens
        }


if __name__ == "__main__":
    # Quick pipeline smoke test
    pipeline = HybridDiagnosticPipeline()
    res = pipeline.run_diagnosis(
        case_id="CASE-01",
        domain="VLAN",
        symptom="PC-Sales-1 cannot reach Server at 192.168.10.100",
        topology_notes="Switch SW-Floor1. PC on Fa0/5 (VLAN 10).",
        show_outputs="SW-Floor1# show interfaces FastEthernet0/5 switchport\nAccess Mode VLAN: 20 (Guest)\nOperational Mode: static access"
    )
    print("Pipeline Output Test:")
    print(f"Case: {res['case_id']} | Overall Confidence: {res['overall_confidence_score']}% | Latency: {res['latency_seconds']}s")
    print(f"Root Cause: {res['ai_diagnosis']['root_cause']}")
    print(f"Lint Score: {res['lint_results']['quality_score']} (Safe: {res['lint_results']['is_safe']})")
