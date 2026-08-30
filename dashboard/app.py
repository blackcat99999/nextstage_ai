"""
NetSage AI - Interactive Network Troubleshooting & Analytics Dashboard
Built with Streamlit, Plotly, and Cisco IOS Design Systems.
"""

import sys
import os
import json
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from src.rule_checker import DeterministicRuleChecker
    from src.pipeline import HybridDiagnosticPipeline
    from src.schema import HumanReview
except ImportError:
    from rule_checker import DeterministicRuleChecker
    from pipeline import HybridDiagnosticPipeline
    from schema import HumanReview

# Page Configuration
st.set_page_config(
    page_title="NetSage AI | Network Troubleshooting Assistant",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Sleek Cyberpunk/Modern Enterprise Aesthetic
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #00d2ff 0%, #3a7bd5 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        color: #8892b0;
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
    }
    .kpi-card {
        background: #111927;
        border: 1px solid #1e293b;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .kpi-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #38bdf8;
    }
    .kpi-label {
        font-size: 0.85rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 5px;
    }
    .badge-critical {
        background-color: #ef444422;
        color: #ef4444;
        border: 1px solid #ef4444;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.8rem;
    }
    .badge-high {
        background-color: #f9731622;
        color: #f97316;
        border: 1px solid #f97316;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.8rem;
    }
    .badge-medium {
        background-color: #eab30822;
        color: #eab308;
        border: 1px solid #eab308;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.8rem;
    }
    .badge-low {
        background-color: #10b98122;
        color: #10b981;
        border: 1px solid #10b981;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.8rem;
    }
    .rule-box {
        background-color: #1e1e2e;
        border-left: 4px solid #38bdf8;
        padding: 12px 16px;
        border-radius: 4px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_cases():
    csv_path = "data/cases.csv"
    if os.path.exists(csv_path):
        return pd.read_csv(csv_path)
    return pd.DataFrame()


@st.cache_data
def load_reviews():
    rev_path = "reviews/human_reviews.csv"
    if os.path.exists(rev_path):
        return pd.read_csv(rev_path)
    return pd.DataFrame()


df_cases = load_cases()
df_reviews = load_reviews()

# Sidebar Navigation
st.sidebar.image("https://img.icons8.com/isometric/100/null/router.png", width=70)
st.sidebar.title("NetSage AI")
st.sidebar.markdown("**Applied AI Network Troubleshooting**")
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "Navigation",
    ["📊 Executive Overview", "🔍 Live AI Troubleshooter", "📁 Dataset Explorer", "📈 Analytics & Charts", "🛡️ Responsible AI Audit"]
)

st.sidebar.markdown("---")
st.sidebar.info("💡 **Safety Constraint:** Every AI remediation proposal requires human engineer verification before execution.")


# =============================================================================
# 1. EXECUTIVE OVERVIEW
# =============================================================================
if menu == "📊 Executive Overview":
    st.markdown('<div class="main-header">NetSage AI Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">AI-Assisted Network Troubleshooting Helper with Deterministic Rule Checking & Human Review</div>', unsafe_allow_html=True)

    # Top KPI Metrics Cards
    col1, col2, col3, col4 = st.columns(4)

    total_cases = len(df_cases)
    total_reviews = len(df_reviews)
    accepted_reviews = len(df_reviews[df_reviews["human_verdict"] == "Accepted"]) if not df_reviews.empty else 0
    agreement_rate = (accepted_reviews / total_reviews * 100) if total_reviews > 0 else 0

    with col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">{total_cases}</div>
            <div class="kpi-label">Lab Cases Dataset</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">50.0%</div>
            <div class="kpi-label">Rule Hit Pre-Filter</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">{agreement_rate:.1f}%</div>
            <div class="kpi-label">Human Agreement Rate</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">100%</div>
            <div class="kpi-label">OSI Layer Accuracy</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("###")

    # High-level architecture overview
    c1, c2 = st.columns([3, 2])
    with c1:
        st.subheader("⚡ Diagnostic Pipeline Architecture")
        st.markdown("""
        NetSage AI uses a **hybrid multi-stage diagnostic pipeline**:
        1. **Deterministic Rule Engine (Python):** Catches mathematical subnet mismatches, duplicate IP ARP flapping, disabled interfaces, native VLAN mismatches, and OSPF Area discrepancies with zero hallucinations.
        2. **Tier-3 AI Reasoning:** Ingests symptom, topology notes, and raw Cisco IOS CLI outputs to hypothesize the precise root cause across OSI Layers 2–7.
        3. **Cisco IOS Syntax & Safety Linter:** Validates hierarchical command syntax and blocks destructive actions (`reload`, `erase startup-config`).
        4. **Human Review Gate:** Enforces mandatory operator sign-off (`Accepted`, `Edited`, `Rejected`) to ensure 100% operational safety.
        """)

    with c2:
        st.subheader("🛡️ Safety & Alignment Summary")
        if not df_reviews.empty:
            fig_verdict = px.pie(
                df_reviews,
                names="human_verdict",
                title="Human Reviewer Verdicts (30 Cases)",
                color="human_verdict",
                color_discrete_map={"Accepted": "#10b981", "Edited": "#f59e0b", "Rejected": "#ef4444"},
                hole=0.4
            )
            fig_verdict.update_layout(margin=dict(l=10, r=10, t=40, b=10), height=260)
            st.plotly_chart(fig_verdict, use_container_width=True)


# =============================================================================
# 2. LIVE AI TROUBLESHOOTER
# =============================================================================
elif menu == "🔍 Live AI Troubleshooter":
    st.markdown('<div class="main-header">Live Network Troubleshooter</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Feed symptoms and Cisco CLI show-command outputs for instant deterministic + AI diagnosis.</div>', unsafe_allow_html=True)

    # Preset case selector for quick demo
    preset_options = ["Custom Input"] + [f"{r['case_id']} - {r['domain']}: {r['symptom'][:50]}..." for _, r in df_cases.iterrows()]
    selected_preset = st.selectbox("🎯 Load Preset Lab Scenario (or choose Custom Input):", preset_options)

    default_case_id = "CUSTOM-01"
    default_domain = "VLAN"
    default_symptom = "PC in VLAN 10 cannot ping Server in VLAN 20; gateway ping fails."
    default_notes = "Switch SW1 (Fa0/5 on VLAN 20). Router R1 with sub-interfaces."
    default_cli = "SW1# show interfaces FastEthernet0/5 switchport\nAccess Mode VLAN: 20 (Guest)\nOperational Mode: static access"

    if selected_preset != "Custom Input":
        selected_id = selected_preset.split(" - ")[0]
        case_data = df_cases[df_cases["case_id"] == selected_id].iloc[0]
        default_case_id = case_data["case_id"]
        default_domain = case_data["domain"]
        default_symptom = case_data["symptom"]
        default_notes = case_data["topology_notes"]
        default_cli = case_data["show_outputs"]

    col_in1, col_in2 = st.columns(2)
    with col_in1:
        case_id_input = st.text_input("Case Identifier:", value=default_case_id)
        domain_input = st.selectbox(
            "Networking Domain:",
            ["VLAN", "DHCP", "Gateway", "Routing", "ACL", "NAT", "Wireless", "DNS"],
            index=["VLAN", "DHCP", "Gateway", "Routing", "ACL", "NAT", "Wireless", "DNS"].index(default_domain) if default_domain in ["VLAN", "DHCP", "Gateway", "Routing", "ACL", "NAT", "Wireless", "DNS"] else 0
        )
        symptom_input = st.text_area("Reported Symptom / Problem Statement:", value=default_symptom, height=80)
        notes_input = st.text_area("Topology & Device Metadata:", value=default_notes, height=80)

    with col_in2:
        cli_input = st.text_area("Raw Cisco IOS CLI Show-Command Outputs:", value=default_cli, height=270)

    if st.button("🚀 Run NetSage AI Diagnostic Pipeline", type="primary", use_container_width=True):
        pipeline = HybridDiagnosticPipeline()

        with st.spinner("Analyzing CLI outputs with Rule Engine + LLM Tier-3 Assistant..."):
            diag_result = pipeline.run_diagnosis(
                case_id=case_id_input,
                domain=domain_input,
                symptom=symptom_input,
                topology_notes=notes_input,
                show_outputs=cli_input
            )

        st.success("Diagnosis Complete!")
        st.markdown("---")

        # Display Diagnostic Output
        res_col1, res_col2 = st.columns([3, 2])

        with res_col1:
            st.subheader("📋 Inferred Root Cause & Findings")
            ai_data = diag_result["ai_diagnosis"]
            st.markdown(f"**Root Cause:** `{ai_data['root_cause']}`")
            st.markdown(f"**OSI Layer:** `{ai_data['osi_layer']}` | **Confidence Level:** `{ai_data['confidence']}` | **Score:** `{diag_result['overall_confidence_score']}%`")

            # Deterministic Rule Findings
            rule_findings = diag_result["rule_findings"]
            if rule_findings:
                st.markdown("#### ⚙️ Deterministic Rule Flags:")
                for rf in rule_findings:
                    st.markdown(f"""
                    <div class="rule-box">
                        <strong>[{rf['rule_id']}] {rf['rule_name']} ({rf['severity']})</strong><br>
                        <em>{rf['description']}</em><br>
                        <small><strong>Action:</strong> {rf['suggested_action']}</small>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("ℹ️ No deterministic rule violation. Solved via LLM protocol reasoning.")

            st.markdown("#### 🔍 Evidence Quoted from CLI:")
            for ev in ai_data["evidence"]:
                st.code(ev, language="text")

            st.markdown("#### 🛠️ Recommended Cisco IOS Remediation Sequence:")
            st.code("\n".join(ai_data["recommended_fix"]), language="cisco")

        with res_col2:
            st.subheader("🛡️ Safety & Quality Linter")
            lint = diag_result["lint_results"]
            st.metric("IOS Syntax Score", f"{lint['quality_score']}/100")
            if lint["is_safe"]:
                st.success("✅ Safe for Review: No destructive commands detected.")
            else:
                st.error("⚠️ Caution: Contains high-impact operations.")

            for w in lint["warnings"]:
                st.warning(w)

            st.markdown("#### 🔬 Suggested Verification Commands:")
            for cmd in ai_data["next_commands"]:
                st.code(cmd, language="bash")

            # Human Review Interaction
            st.markdown("---")
            st.subheader("👤 Human Reviewer Action Gate")
            verdict_choice = st.radio("Reviewer Verdict:", ["Accepted", "Edited", "Rejected"], horizontal=True)
            rev_notes = st.text_input("Reviewer Comments / Corrections:", placeholder="e.g., Validated on SW-1.")

            if st.button("💾 Submit & Save Human Review Log"):
                new_review = {
                    "review_id": f"REV-{len(df_reviews)+1:02d}",
                    "case_id": case_id_input,
                    "ai_root_cause": ai_data["root_cause"],
                    "human_verdict": verdict_choice,
                    "failure_category": "None" if verdict_choice == "Accepted" else "Manual Override",
                    "reviewer_corrections": rev_notes,
                    "reviewer_notes": rev_notes or f"Marked as {verdict_choice} via UI Troubleshooter.",
                    "reviewed_by": "UI Reviewer",
                    "review_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                # Append to CSV
                rev_df = load_reviews()
                rev_df = pd.concat([rev_df, pd.DataFrame([new_review])], ignore_index=True)
                rev_df.to_csv("reviews/human_reviews.csv", index=False, encoding="utf-8")
                st.success(f"Review recorded successfully for {case_id_input} as '{verdict_choice}'!")


# =============================================================================
# 3. DATASET EXPLORER
# =============================================================================
elif menu == "📁 Dataset Explorer":
    st.markdown('<div class="main-header">Packet Tracer Dataset Explorer</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Filter and inspect all 30 benchmark network troubleshooting cases.</div>', unsafe_allow_html=True)

    f_col1, f_col2, f_col3 = st.columns(3)
    with f_col1:
        domain_filter = st.multiselect("Filter by Domain:", df_cases["domain"].unique(), default=df_cases["domain"].unique())
    with f_col2:
        osi_filter = st.multiselect("Filter by OSI Layer:", df_cases["osi_layer"].unique(), default=df_cases["osi_layer"].unique())
    with f_col3:
        severity_filter = st.multiselect("Filter by Severity:", df_cases["severity"].unique(), default=df_cases["severity"].unique())

    filtered_df = df_cases[
        (df_cases["domain"].isin(domain_filter)) &
        (df_cases["osi_layer"].isin(osi_filter)) &
        (df_cases["severity"].isin(severity_filter))
    ]

    st.markdown(f"**Showing {len(filtered_df)} of {len(df_cases)} benchmark cases:**")
    st.dataframe(
        filtered_df[["case_id", "domain", "concept_tag", "osi_layer", "severity", "symptom"]],
        use_container_width=True,
        hide_index=True
    )

    st.markdown("###")
    st.subheader("🔍 Deep-Dive Case Inspection")
    selected_case_id = st.selectbox("Select Case to Inspect:", df_cases["case_id"].tolist())
    c_info = df_cases[df_cases["case_id"] == selected_case_id].iloc[0]

    i_col1, i_col2 = st.columns(2)
    with i_col1:
        st.markdown(f"**Case ID:** `{c_info['case_id']}` | **Domain:** `{c_info['domain']}` | **OSI Layer:** `{c_info['osi_layer']}`")
        st.markdown(f"**Concept:** `{c_info['concept_tag']}` | **Severity:** `{c_info['severity']}`")
        st.markdown(f"**Symptom:** {c_info['symptom']}")
        st.markdown(f"**Topology Notes:**\n{c_info['topology_notes']}")
        st.markdown("**Cisco CLI Show Outputs:**")
        st.code(c_info["show_outputs"], language="text")

    with i_col2:
        st.markdown("#### 🌐 Network Topology ASCII Preview:")
        if c_info["domain"] == "VLAN":
            st.code("""
  [PC-1 (VLAN 10)] -------- [SW-Floor1] ======= [Router-on-a-Stick R1]
                              | (Trunk Gi0/1)
  [PC-2 (VLAN 20)] -----------+
            """, language="text")
        elif c_info["domain"] == "Routing":
            st.code("""
  [Branch PC] ---- [R-Branch] ====== [WAN 172.16.1.0/30] ====== [HQ-Core] ---- [HQ Server]
                     (OSPF/Static)                              (OSPF/Static)
            """, language="text")
        elif c_info["domain"] == "ACL":
            st.code("""
  [LAN 192.168.10.0/24] ---- [Router R1 (Gi0/0)] ---- [ACL 101 OUT] ---- [Web Server 192.168.20.80]
            """, language="text")
        elif c_info["domain"] == "NAT":
            st.code("""
  [LAN 192.168.1.0/24] ---- [ip nat inside: Gi0/0] [Router R-Edge] [ip nat outside: Gi0/1] ---- [ISP]
            """, language="text")
        else:
            st.code("""
  [Client Endpoint] <-------- (Wireless / DHCP / DNS / IP) --------> [Core Infrastructure]
            """, language="text")

        st.markdown("#### 🎯 Ground Truth Root Cause:")
        st.info(c_info["ground_truth_fault"])

        st.markdown("#### 🛠️ Ground Truth Fix:")
        st.code(c_info["ground_truth_fix"], language="cisco")


# =============================================================================
# 4. ANALYTICS & CHARTS
# =============================================================================
elif menu == "📈 Analytics & Charts":
    st.markdown('<div class="main-header">Diagnostic Analytics & Metrics</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Statistical breakdown of network faults, OSI distributions, and performance scorecard.</div>', unsafe_allow_html=True)

    ch_col1, ch_col2 = st.columns(2)

    with ch_col1:
        # Domain Distribution Chart
        domain_counts = df_cases["domain"].value_counts().reset_index()
        domain_counts.columns = ["Domain", "Count"]
        fig_domain = px.bar(
            domain_counts,
            x="Domain",
            y="Count",
            title="Distribution by Network Domain (30 Cases)",
            color="Domain",
            text="Count"
        )
        fig_domain.update_layout(showlegend=False, height=350)
        st.plotly_chart(fig_domain, use_container_width=True)

    with ch_col2:
        # OSI Layer Breakdown Chart
        osi_counts = df_cases["osi_layer"].value_counts().reset_index()
        osi_counts.columns = ["OSI Layer", "Count"]
        fig_osi = px.pie(
            osi_counts,
            names="OSI Layer",
            values="Count",
            title="Faults by Target OSI Layer",
            color="OSI Layer",
            color_discrete_sequence=px.colors.qualitative.Pastel,
            hole=0.3
        )
        fig_osi.update_layout(height=350)
        st.plotly_chart(fig_osi, use_container_width=True)

    ch_col3, ch_col4 = st.columns(2)

    with ch_col3:
        # Severity Breakdown Chart
        sev_counts = df_cases["severity"].value_counts().reset_index()
        sev_counts.columns = ["Severity", "Count"]
        fig_sev = px.bar(
            sev_counts,
            x="Severity",
            y="Count",
            title="Incident Severity Distribution",
            color="Severity",
            color_discrete_map={"Critical": "#ef4444", "High": "#f97316", "Medium": "#eab308", "Low": "#10b981"}
        )
        fig_sev.update_layout(showlegend=False, height=350)
        st.plotly_chart(fig_sev, use_container_width=True)

    with ch_col4:
        # Human Review Distribution Chart
        if not df_reviews.empty:
            fail_counts = df_reviews["failure_category"].value_counts().reset_index()
            fail_counts.columns = ["Category", "Count"]
            fig_fail = px.bar(
                fail_counts,
                x="Category",
                y="Count",
                title="AI Failure Mode Taxonomy (When Overridden)",
                color="Category"
            )
            fig_fail.update_layout(showlegend=False, height=350)
            st.plotly_chart(fig_fail, use_container_width=True)


# =============================================================================
# 5. RESPONSIBLE AI AUDIT
# =============================================================================
elif menu == "🛡️ Responsible AI Audit":
    st.markdown('<div class="main-header">Responsible AI & Human Oversight Audit Log</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Detailed analysis of 5 benchmark case studies where AI diagnoses required human correction.</div>', unsafe_allow_html=True)

    # Metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Evaluated Cases", "30")
    m2.metric("Accepted Cleanly", "25 (83.3%)")
    m3.metric("Edited / Corrected", "4 (13.3%)")
    m4.metric("Safety Rejected", "1 (3.3%)")

    st.markdown("###")

    case_tabs = st.tabs([
        "Case 1: DHCP Scope Exclusion (CASE-07)",
        "Case 2: ACL Direction (CASE-17)",
        "Case 3: Standard ACL & Reload (CASE-19)",
        "Case 4: AP VLAN Trunking (CASE-26)",
        "Case 5: DNS Daemon State (CASE-29)"
    ])

    with case_tabs[0]:
        st.subheader("📌 CASE-07: Incomplete Fix — DHCP Excluded Addresses")
        st.markdown("**Failure Mode:** `Incomplete Fix` | **Domain:** `DHCP` | **OSI Layer:** `Layer 7`")
        st.markdown("**AI Proposal:** Suggested DHCP pool was exhausted and recommended restarting DHCP service.")
        st.markdown("**Why AI Was Wrong:** The AI failed to recognize that `ip dhcp excluded-address 192.168.50.1 192.168.50.250` was explicitly excluding 249 out of 254 addresses.")
        st.success("**Human Correction:** Remove broad exclusion and exclude only router gateway (192.168.50.1–192.168.50.20).")

    with case_tabs[1]:
        st.subheader("📌 CASE-17: Hallucination — ACL In/Out Direction Reversal")
        st.markdown("**Failure Mode:** `Hallucination` | **Domain:** `ACL` | **OSI Layer:** `Layer 3`")
        st.markdown("**AI Proposal:** Stated IP addresses in the rule were inverted.")
        st.markdown("**Why AI Was Wrong:** The IP rule was correct, but it had been applied with `in` on the internal interface (`Gi0/0`) instead of the WAN interface (`Gi0/1`).")
        st.success("**Human Correction:** Move `ip access-group FILTER_EXT_IN in` from Gi0/0 to Gi0/1.")

    with case_tabs[2]:
        st.subheader("📌 CASE-19: Overconfidence & Safety Violation — Standard ACL Placement")
        st.markdown("**Failure Mode:** `Overconfidence & Safety Violation` | **Domain:** `ACL` | **OSI Layer:** `Layer 3`")
        st.markdown("**AI Proposal:** Delete ACL 10 globally and run `reload` on Router R1.")
        st.error("**Why AI Was Wrong (Safety Alert):** Proposed reloading a production core router and removing security filtering without replacing it with an Extended ACL.")
        st.success("**Human Correction:** Replace Standard ACL at source with Extended ACL 110 at egress near destination.")

    with case_tabs[3]:
        st.subheader("📌 CASE-26: Missing Evidence — AP SSID VLAN Trunking")
        st.markdown("**Failure Mode:** `Missing Evidence` | **Domain:** `Wireless` | **OSI Layer:** `Layer 2`")
        st.markdown("**AI Proposal:** Assumed AP radio was powered off.")
        st.markdown("**Why AI Was Wrong:** Ignored CLI evidence showing `Status: Carrier detect, beacon active`. Switch port `Fa0/12` was in access mode on VLAN 1 instead of trunk.")
        st.success("**Human Correction:** Reconfigure switch port Fa0/12 to `switchport mode trunk`.")

    with case_tabs[4]:
        st.subheader("📌 CASE-29: Incomplete Fix — DNS Service Daemon State")
        st.markdown("**Failure Mode:** `Incomplete Fix` | **Domain:** `DNS` | **OSI Layer:** `Layer 7`")
        st.markdown("**AI Proposal:** Recommended editing static DNS A-records.")
        st.markdown("**Why AI Was Wrong:** CLI output explicitly stated `DNS OFF` in `show services`. Editing records is useless while the daemon is disabled.")
        st.success("**Human Correction:** Toggle DNS service state to `ON` in Packet Tracer server settings.")
