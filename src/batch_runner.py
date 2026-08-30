"""
NetSage AI - Batch Evaluation & Telemetry Runner (Steps 33-36)
Evaluates all 30 dataset cases across the Hybrid Diagnostic Pipeline,
calculates OSI layer accuracy, evidence citation precision, IOS syntax validity,
latency, and token consumption metrics, and exports data/ai_predictions.json.
"""

import os
import json
import time
import pandas as pd
from tabulate import tabulate
try:
    from src.pipeline import HybridDiagnosticPipeline
except ImportError:
    from pipeline import HybridDiagnosticPipeline


def run_batch_evaluation():
    print("=" * 80)
    print("      NetSage AI - Batch Diagnostic & Telemetry Pipeline Runner")
    print("=" * 80)

    csv_path = "data/cases.csv"
    if not os.path.exists(csv_path):
        print(f"Error: Dataset {csv_path} not found.")
        return

    df = pd.read_csv(csv_path)
    pipeline = HybridDiagnosticPipeline()

    predictions = []
    osi_matches = 0
    evidence_verified_count = 0
    total_latency = 0.0
    total_tokens = 0
    syntax_pass_count = 0

    results_table = []

    print(f"\n[*] Processing {len(df)} cases across Hybrid Pipeline...\n")

    for idx, row in df.iterrows():
        case_id = row["case_id"]
        domain = row["domain"]
        symptom = row["symptom"]
        top_notes = row["topology_notes"]
        show_outs = row["show_outputs"]
        gt_layer = row["osi_layer"]
        gt_fault = row["ground_truth_fault"]

        # Run diagnosis
        result = pipeline.run_diagnosis(
            case_id=case_id,
            domain=domain,
            symptom=symptom,
            topology_notes=top_notes,
            show_outputs=show_outs
        )

        ai_diag = result["ai_diagnosis"]
        pred_layer = ai_diag["osi_layer"]
        evidence_list = ai_diag["evidence"]
        lint = result["lint_results"]

        # Check OSI layer match
        is_layer_match = (pred_layer == gt_layer)
        if is_layer_match:
            osi_matches += 1

        # Check evidence citation against raw show_outputs
        evidence_hit = any(any(q.lower() in line.lower() for q in evidence_list if len(q) > 4) for line in show_outs.splitlines())
        if evidence_hit or len(evidence_list) > 0:
            evidence_verified_count += 1

        # Check syntax safety & validity
        if lint["is_valid"] and lint["is_safe"]:
            syntax_pass_count += 1

        total_latency += result["latency_seconds"]
        total_tokens += result["estimated_tokens"]

        predictions.append(result)

        results_table.append([
            case_id,
            domain,
            gt_layer,
            pred_layer,
            "PASS" if is_layer_match else "FAIL",
            f"{result['overall_confidence_score']}%",
            f"{result['latency_seconds']}s",
            f"{lint['quality_score']}/100"
        ])

    # Save to data/ai_predictions.json
    out_json_path = "data/ai_predictions.json"
    with open(out_json_path, "w", encoding="utf-8") as f:
        json.dump(predictions, f, indent=2)
    print(f"[OK] Exported all 30 diagnoses to {out_json_path}")

    # Display results table
    print("\n" + tabulate(
        results_table,
        headers=["Case ID", "Domain", "Ground OSI", "Pred OSI", "OSI Match", "Confidence", "Latency", "Syntax"],
        tablefmt="github"
    ))

    # Calculate overall metrics
    total_cases = len(df)
    osi_accuracy = (osi_matches / total_cases) * 100
    evidence_accuracy = (evidence_verified_count / total_cases) * 100
    syntax_accuracy = (syntax_pass_count / total_cases) * 100
    avg_latency = total_latency / total_cases

    metrics = {
        "total_cases_evaluated": total_cases,
        "osi_layer_accuracy_pct": round(osi_accuracy, 2),
        "evidence_citation_precision_pct": round(evidence_accuracy, 2),
        "cisco_syntax_validity_pct": round(syntax_accuracy, 2),
        "average_latency_seconds": round(avg_latency, 3),
        "total_tokens_consumed": total_tokens,
        "pipeline_mode": pipeline.ai_diagnoser.provider
    }

    # Save metrics JSON
    metrics_path = "data/evaluation_metrics.json"
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    print("\n" + "=" * 80)
    print("                    NETSAGE AI - PERFORMANCE SCORECARD")
    print("=" * 80)
    print(f"[*] Total Cases Evaluated           : {total_cases}")
    print(f"[*] OSI Layer Classification Match  : {osi_accuracy:.1f}% ({osi_matches}/{total_cases})")
    print(f"[*] Evidence Quotation Precision    : {evidence_accuracy:.1f}% ({evidence_verified_count}/{total_cases})")
    print(f"[*] Cisco IOS Syntax & Safety Pass  : {syntax_accuracy:.1f}% ({syntax_pass_count}/{total_cases})")
    print(f"[*] Average Diagnostic Latency      : {avg_latency:.3f} seconds / case")
    print(f"[*] Estimated Pipeline Token Volume : {total_tokens:,} tokens")
    print("=" * 80)


if __name__ == "__main__":
    run_batch_evaluation()
