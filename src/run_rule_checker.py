"""
NetSage AI - Rule Checker CLI & Dataset Evaluation Runner
Runs the deterministic rule engine over all 30 dataset cases and prints structured findings.
"""

import os
import json
import pandas as pd
from tabulate import tabulate
try:
    from src.rule_checker import DeterministicRuleChecker
except ImportError:
    from rule_checker import DeterministicRuleChecker


def run_rule_evaluation():
    print("=" * 75)
    print("       NetSage AI - Deterministic Rule Checker CLI Engine")
    print("=" * 75)

    csv_path = "data/cases.csv"
    if not os.path.exists(csv_path):
        print(f"Error: Dataset not found at {csv_path}")
        return

    df = pd.read_csv(csv_path)
    checker = DeterministicRuleChecker()

    results_table = []
    total_findings = 0
    cases_with_findings = 0

    for _, row in df.iterrows():
        case_id = row["case_id"]
        domain = row["domain"]
        symptom = row["symptom"]
        top_notes = row["topology_notes"]
        show_outs = row["show_outputs"]

        findings = checker.evaluate_all(show_outs, top_notes, symptom)
        if findings:
            cases_with_findings += 1
            total_findings += len(findings)
            rule_names = ", ".join([f"{f.rule_id} ({f.severity})" for f in findings])
            primary_action = findings[0].suggested_action
        else:
            rule_names = "No deterministic rule matched (requires AI heuristic)"
            primary_action = "Invoke LLM Tier-3 Assistant"

        results_table.append([case_id, domain, rule_names, primary_action[:45] + "..."])

    print(tabulate(
        results_table,
        headers=["Case ID", "Domain", "Rule Triggers", "Suggested Action"],
        tablefmt="github"
    ))

    print("\n" + "=" * 75)
    print(f"[*] Total Cases Evaluated: {len(df)}")
    print(f"[*] Cases Triggering Deterministic Rules: {cases_with_findings} ({cases_with_findings/len(df)*100:.1f}%)")
    print(f"[*] Total Rule Violations Flagged: {total_findings}")
    print("=" * 75)


if __name__ == "__main__":
    run_rule_evaluation()
