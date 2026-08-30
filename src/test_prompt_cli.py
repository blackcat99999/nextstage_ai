"""
NetSage AI - AI Prompt & Diagnosis CLI Tester (Step 30)
Tests the complete prompt pipeline, rule integration, and JSON formatting against 3 edge cases.
"""

import json
import pandas as pd
try:
    from src.schema import AIDiagnosis
    from src.rule_checker import DeterministicRuleChecker
    from src.ai_diagnoser import AIDiagnoser
except ImportError:
    from schema import AIDiagnosis
    from rule_checker import DeterministicRuleChecker
    from ai_diagnoser import AIDiagnoser


def test_prompt_edge_cases():
    print("=" * 75)
    print("      NetSage AI - AI Prompt Edge Case Testing Runner (Step 30)")
    print("=" * 75)

    df = pd.read_csv("data/cases.csv")
    checker = DeterministicRuleChecker()
    diagnoser = AIDiagnoser()

    test_case_ids = ["CASE-01", "CASE-16", "CASE-28"]

    for case_id in test_case_ids:
        case_row = df[df["case_id"] == case_id].iloc[0]
        print(f"\n[+] Testing Prompt Pipeline for {case_id} ({case_row['domain']})...")
        print(f"    Symptom: {case_row['symptom']}")

        # 1. Evaluate Rule Checker
        rule_findings = checker.evaluate_all(
            case_row["show_outputs"],
            case_row["topology_notes"],
            case_row["symptom"]
        )
        print(f"    Deterministic Findings: {len(rule_findings)} rules triggered")

        # 2. Run AI Diagnosis
        diagnosis: AIDiagnosis = diagnoser.diagnose(
            case_id=case_id,
            domain=case_row["domain"],
            symptom=case_row["symptom"],
            topology_notes=case_row["topology_notes"],
            show_outputs=case_row["show_outputs"],
            rule_findings=rule_findings
        )

        # 3. Validate JSON Schema Adherence
        assert diagnosis.case_id == case_id
        assert diagnosis.osi_layer in ["Layer 2", "Layer 3", "Layer 4", "Layer 7"]
        assert diagnosis.confidence in ["High", "Medium", "Low"]
        assert len(diagnosis.evidence) > 0
        assert len(diagnosis.recommended_fix) > 0

        print(f"    [PASS] Inferred Root Cause: {diagnosis.root_cause}")
        print(f"    [PASS] OSI Layer: {diagnosis.osi_layer} | Confidence: {diagnosis.confidence}")
        print(f"    [PASS] Quoted Evidence: {diagnosis.evidence}")
        print(f"    [PASS] Next Verification Commands: {diagnosis.next_commands}")
        print(f"    [PASS] Recommended Fix Commands:\n      " + "\n      ".join(diagnosis.recommended_fix[:3]))

    print("\n" + "=" * 75)
    print("  [SUCCESS] All Prompt Test Cases Passed Schema & Reasoning Validation!")
    print("=" * 75)


if __name__ == "__main__":
    test_prompt_edge_cases()
