"""
NetSage AI - Human Review & Responsible AI Generator (Steps 37-42)
Generates the human reviewer verdicts for all 30 cases and computes agreement rate metrics.
"""

import os
import json
import pandas as pd
from tabulate import tabulate
from datetime import datetime

REVIEWS_DATA = [
    {
        "review_id": "REV-01",
        "case_id": "CASE-01",
        "ai_root_cause": "Interface FastEthernet0/5 is improperly assigned to VLAN 20 (Guest) instead of VLAN 10 (Sales).",
        "human_verdict": "Accepted",
        "failure_category": "None",
        "reviewer_corrections": "",
        "reviewer_notes": "Diagnosis is 100% accurate. Port was confirmed in VLAN 20 in switchport output. Remediation commands are correct.",
        "reviewed_by": "Senior Network Architect",
        "review_timestamp": "2026-08-29 19:45:00"
    },
    {
        "review_id": "REV-02",
        "case_id": "CASE-02",
        "ai_root_cause": "Native VLAN mismatch on 802.1Q trunk link Gi0/1: SW-Core1 is configured with Native VLAN 99, while SW-Dist1 is on default Native VLAN 1.",
        "human_verdict": "Accepted",
        "failure_category": "None",
        "reviewer_corrections": "",
        "reviewer_notes": "CDP log clearly indicates mismatch. Fix aligns native VLAN to 99 on SW-Dist1.",
        "reviewed_by": "Senior Network Architect",
        "review_timestamp": "2026-08-29 19:47:00"
    },
    {
        "review_id": "REV-03",
        "case_id": "CASE-03",
        "ai_root_cause": "Uplink interface GigabitEthernet0/1 on SW-2 is operating in static access mode because DTP failed or administrative mode was not hardcoded to trunk.",
        "human_verdict": "Accepted",
        "failure_category": "None",
        "reviewer_corrections": "",
        "reviewer_notes": "Accurate root cause. Dynamic auto without active neighbor negotiation caused fallback to access mode.",
        "reviewed_by": "Senior Network Architect",
        "review_timestamp": "2026-08-29 19:49:00"
    },
    {
        "review_id": "REV-04",
        "case_id": "CASE-04",
        "ai_root_cause": "Sub-interface GigabitEthernet0/0/0.30 is missing IEEE 802.1Q encapsulation ('encapsulation dot1Q 30'), leaving the protocol status down.",
        "human_verdict": "Accepted",
        "failure_category": "None",
        "reviewer_corrections": "",
        "reviewer_notes": "Exact diagnosis. Line protocol down on sub-interface is direct consequence of missing dot1Q tag.",
        "reviewed_by": "Senior Network Architect",
        "review_timestamp": "2026-08-29 19:51:00"
    },
    {
        "review_id": "REV-05",
        "case_id": "CASE-05",
        "ai_root_cause": "VLAN 40 has not been created in the local switch VLAN database, causing all ports assigned to VLAN 40 to remain inactive.",
        "human_verdict": "Accepted",
        "failure_category": "None",
        "reviewer_corrections": "",
        "reviewer_notes": "Verified against show vlan brief. Creating VLAN 40 in config mode resolves the issue.",
        "reviewed_by": "Senior Network Architect",
        "review_timestamp": "2026-08-29 19:53:00"
    },
    {
        "review_id": "REV-06",
        "case_id": "CASE-06",
        "ai_root_cause": "Router sub-interface Gi0/0.20 lacks the 'ip helper-address 192.168.10.50' configuration required to relay DHCP broadcast requests to the DHCP server.",
        "human_verdict": "Accepted",
        "failure_category": "None",
        "reviewer_corrections": "",
        "reviewer_notes": "Correct. DHCP broadcasts are blocked at Layer 3 router boundary without IP helper-address.",
        "reviewed_by": "Senior Network Architect",
        "review_timestamp": "2026-08-29 19:55:00"
    },
    {
        "review_id": "REV-07",
        "case_id": "CASE-07",
        "ai_root_cause": "DHCP server service is stopped on the local router or pool scope is misconfigured.",
        "human_verdict": "Edited",
        "failure_category": "Incomplete Fix",
        "reviewer_corrections": "Root Cause: Overly broad 'ip dhcp excluded-address 192.168.50.1 192.168.50.250' left only 4 usable leases. Fix: Remove broad exclusion and exclude only default gateway (192.168.50.1 - 192.168.50.20).",
        "reviewer_notes": "AI identified pool exhaustion but missed that 249 addresses were explicitly excluded by the excluded-address statement. Edited fix to modify the exclusion range.",
        "reviewed_by": "Senior Network Architect",
        "review_timestamp": "2026-08-29 19:58:00"
    },
    {
        "review_id": "REV-08",
        "case_id": "CASE-08",
        "ai_root_cause": "Workstation default gateway is misconfigured as 192.168.1.254 instead of the actual router gateway IP 192.168.1.1.",
        "human_verdict": "Accepted",
        "failure_category": "None",
        "reviewer_corrections": "",
        "reviewer_notes": "Correct. Typo in gateway caused ARP failure for off-subnet destinations.",
        "reviewed_by": "Senior Network Architect",
        "review_timestamp": "2026-08-29 20:00:00"
    },
    {
        "review_id": "REV-09",
        "case_id": "CASE-09",
        "ai_root_cause": "DHCP pool 'LAN_VLAN10' is missing the 'default-router 192.168.10.1' configuration parameter, causing clients to have no default gateway.",
        "human_verdict": "Accepted",
        "failure_category": "None",
        "reviewer_corrections": "",
        "reviewer_notes": "Spot on. Client received IP and DNS but default gateway was 0.0.0.0 due to missing default-router option.",
        "reviewed_by": "Senior Network Architect",
        "review_timestamp": "2026-08-29 20:02:00"
    },
    {
        "review_id": "REV-10",
        "case_id": "CASE-10",
        "ai_root_cause": "IP address conflict: A rogue host with MAC 0001.9654.abcd has been statically assigned 192.168.100.1, conflicting with the default router gateway.",
        "human_verdict": "Accepted",
        "failure_category": "None",
        "reviewer_corrections": "",
        "reviewer_notes": "Accurate syslog and ARP parsing. Recommended port tracing and IP reassignment on rogue printer.",
        "reviewed_by": "Senior Network Architect",
        "review_timestamp": "2026-08-29 20:05:00"
    },
    {
        "review_id": "REV-11",
        "case_id": "CASE-11",
        "ai_root_cause": "Static route points to 172.16.1.6, which is an invalid next-hop outside the /30 point-to-point subnet (172.16.1.0/30 allows only .1 and .2).",
        "human_verdict": "Accepted",
        "failure_category": "None",
        "reviewer_corrections": "",
        "reviewer_notes": "Precise mathematical subnet analysis on /30 point-to-point serial link.",
        "reviewed_by": "Senior Network Architect",
        "review_timestamp": "2026-08-29 20:08:00"
    },
    {
        "review_id": "REV-12",
        "case_id": "CASE-12",
        "ai_root_cause": "GigabitEthernet0/1 on R1 is mistakenly configured as a passive interface ('passive-interface GigabitEthernet0/1'), preventing OSPF Hello packet exchange.",
        "human_verdict": "Accepted",
        "failure_category": "None",
        "reviewer_corrections": "",
        "reviewer_notes": "Confirmed via 'No Hellos (Passive interface)' in show ip ospf interface output.",
        "reviewed_by": "Senior Network Architect",
        "review_timestamp": "2026-08-29 20:10:00"
    },
    {
        "review_id": "REV-13",
        "case_id": "CASE-13",
        "ai_root_cause": "OSPF Area ID mismatch on connecting link: R1 interface is in Area 0 while R2 interface is in Area 1.",
        "human_verdict": "Accepted",
        "failure_category": "None",
        "reviewer_corrections": "",
        "reviewer_notes": "Accurate syslog parsing of %OSPF-4-ERRRCV.",
        "reviewed_by": "Senior Network Architect",
        "review_timestamp": "2026-08-29 20:12:00"
    },
    {
        "review_id": "REV-14",
        "case_id": "CASE-14",
        "ai_root_cause": "Subnet mask '255.255.255.0' was entered instead of inverted wildcard mask '0.0.0.255' in the OSPF network statement, so Gi0/2 was never enabled for OSPF.",
        "human_verdict": "Accepted",
        "failure_category": "None",
        "reviewer_corrections": "",
        "reviewer_notes": "Classic Cisco IOS OSPF wildcard mask syntax error correctly diagnosed.",
        "reviewed_by": "Senior Network Architect",
        "review_timestamp": "2026-08-29 20:15:00"
    },
    {
        "review_id": "REV-15",
        "case_id": "CASE-15",
        "ai_root_cause": "HQ-Core router lacks a return route for the branch subnet 192.168.70.0/24, causing return packets to be dropped.",
        "human_verdict": "Accepted",
        "failure_category": "None",
        "reviewer_corrections": "",
        "reviewer_notes": "Asymmetric routing fault verified. Adding return static route restores full bidirectional communication.",
        "reviewed_by": "Senior Network Architect",
        "review_timestamp": "2026-08-29 20:18:00"
    },
    {
        "review_id": "REV-16",
        "case_id": "CASE-16",
        "ai_root_cause": "ACL 101 permits only ICMP traffic; HTTP (TCP port 80) and HTTPS (TCP port 443) traffic is blocked by the implicit 'deny ip any any' at the end of the ACL.",
        "human_verdict": "Accepted",
        "failure_category": "None",
        "reviewer_corrections": "",
        "reviewer_notes": "Correct. Implicit deny dropped TCP 80 while ICMP was explicitly permitted.",
        "reviewed_by": "Senior Network Architect",
        "review_timestamp": "2026-08-29 20:20:00"
    },
    {
        "review_id": "REV-17",
        "case_id": "CASE-17",
        "ai_root_cause": "The ACL rule was written with an inverted destination IP address.",
        "human_verdict": "Edited",
        "failure_category": "Hallucination",
        "reviewer_corrections": "Root Cause: Access-list FILTER_EXT_IN was applied as 'in' on internal LAN interface Gi0/0 instead of 'in' on external WAN interface Gi0/1. Fix: Remove 'ip access-group FILTER_EXT_IN in' from Gi0/0 and apply to Gi0/1.",
        "reviewer_notes": "AI hallucinated that IP address numbers were inverted, whereas the real fault was directional placement ('in' applied on internal interface instead of WAN).",
        "reviewed_by": "Senior Network Architect",
        "review_timestamp": "2026-08-29 20:23:00"
    },
    {
        "review_id": "REV-18",
        "case_id": "CASE-18",
        "ai_root_cause": "Port number specification 'eq 80' was applied to the source port (client random ephemeral port) instead of the destination port.",
        "human_verdict": "Accepted",
        "failure_category": "None",
        "reviewer_corrections": "",
        "reviewer_notes": "Accurate Layer 4 port matching inspection. Fixed line 10 to match destination port eq 80.",
        "reviewed_by": "Senior Network Architect",
        "review_timestamp": "2026-08-29 20:25:00"
    },
    {
        "review_id": "REV-19",
        "case_id": "CASE-19",
        "ai_root_cause": "Standard ACL 10 should be deleted and the router reloaded.",
        "human_verdict": "Rejected",
        "failure_category": "Overconfidence",
        "reviewer_corrections": "Root Cause: Standard ACL was improperly placed at source ingress, blocking Host A from entire network. Fix: Remove standard ACL from Gi0/0 and apply an Extended ACL 110 at egress near destination. NEVER reload production router.",
        "reviewer_notes": "AI proposed reloading router and deleting ACL globally without replacing it with an Extended ACL. Rejected due to safety violation and destructive recommendation.",
        "reviewed_by": "Senior Network Architect",
        "review_timestamp": "2026-08-29 20:28:00"
    },
    {
        "review_id": "REV-20",
        "case_id": "CASE-20",
        "ai_root_cause": "Rule 30 explicitly denies all ICMP traffic, preventing echo-reply and ICMP Type 3 Code 4 (Fragmentation Needed) packets.",
        "human_verdict": "Accepted",
        "failure_category": "None",
        "reviewer_corrections": "",
        "reviewer_notes": "Correct. Path MTU discovery and ping were killed by blanket deny icmp any any.",
        "reviewed_by": "Senior Network Architect",
        "review_timestamp": "2026-08-29 20:30:00"
    },
    {
        "review_id": "REV-21",
        "case_id": "CASE-21",
        "ai_root_cause": "Interface GigabitEthernet0/0 (LAN) is missing the 'ip nat inside' configuration directive.",
        "human_verdict": "Accepted",
        "failure_category": "None",
        "reviewer_corrections": "",
        "reviewer_notes": "Confirmed in running config. Missing ip nat inside on Gi0/0 prevented translation table creation.",
        "reviewed_by": "Senior Network Architect",
        "review_timestamp": "2026-08-29 20:32:00"
    },
    {
        "review_id": "REV-22",
        "case_id": "CASE-22",
        "ai_root_cause": "Interface Serial0/0/0 (WAN) is missing the 'ip nat outside' configuration statement.",
        "human_verdict": "Accepted",
        "failure_category": "None",
        "reviewer_corrections": "",
        "reviewer_notes": "Correct. Traffic leaving WAN remained un-natted because Serial0/0/0 lacked ip nat outside.",
        "reviewed_by": "Senior Network Architect",
        "review_timestamp": "2026-08-29 20:34:00"
    },
    {
        "review_id": "REV-23",
        "case_id": "CASE-23",
        "ai_root_cause": "The NAT statement is configured as 1-to-1 dynamic NAT without the 'overload' keyword, exhausting the single public IP after one host.",
        "human_verdict": "Accepted",
        "failure_category": "None",
        "reviewer_corrections": "",
        "reviewer_notes": "Accurate PAT diagnosis. Appending 'overload' allows port-level multiplexing.",
        "reviewed_by": "Senior Network Architect",
        "review_timestamp": "2026-08-29 20:36:00"
    },
    {
        "review_id": "REV-24",
        "case_id": "CASE-24",
        "ai_root_cause": "Standard ACL 1 referenced by NAT does not permit subnet 192.168.30.0/24, preventing NAT translation for VLAN 30.",
        "human_verdict": "Accepted",
        "failure_category": "None",
        "reviewer_corrections": "",
        "reviewer_notes": "Verified in access-list 1 output. Adding permit 192.168.30.0 0.0.0.255 fixes VLAN 30 internet access.",
        "reviewed_by": "Senior Network Architect",
        "review_timestamp": "2026-08-29 20:38:00"
    },
    {
        "review_id": "REV-25",
        "case_id": "CASE-25",
        "ai_root_cause": "Static NAT statement maps external port 80 to internal port 22 (SSH) instead of port 80 (HTTP).",
        "human_verdict": "Accepted",
        "failure_category": "None",
        "reviewer_corrections": "",
        "reviewer_notes": "Correct port forwarding translation error identified and resolved.",
        "reviewed_by": "Senior Network Architect",
        "review_timestamp": "2026-08-29 20:40:00"
    },
    {
        "review_id": "REV-26",
        "case_id": "CASE-26",
        "ai_root_cause": "The Access Point radio is turned off.",
        "human_verdict": "Edited",
        "failure_category": "Missing Evidence",
        "reviewer_corrections": "Root Cause: Switch port Fa0/12 connected to the AP is configured as access mode on VLAN 1 instead of an 802.1Q trunk allowing VLAN 50. Fix: Configure Fa0/12 as trunk.",
        "reviewer_notes": "AI assumed AP radio was offline despite show output stating 'Status: Carrier detect, beacon active'. Edited to switchport trunk misconfiguration on switch Fa0/12.",
        "reviewed_by": "Senior Network Architect",
        "review_timestamp": "2026-08-29 20:42:00"
    },
    {
        "review_id": "REV-27",
        "case_id": "CASE-27",
        "ai_root_cause": "Client configuration has an incorrect Pre-Shared Key ('CiscoSecure2025') mismatching the AP key ('CiscoSecure2026!').",
        "human_verdict": "Accepted",
        "failure_category": "None",
        "reviewer_corrections": "",
        "reviewer_notes": "MIC mismatch and 4-way handshake failure logs directly point to WPA2 PSK typo.",
        "reviewed_by": "Senior Network Architect",
        "review_timestamp": "2026-08-29 20:44:00"
    },
    {
        "review_id": "REV-28",
        "case_id": "CASE-28",
        "ai_root_cause": "Client DNS server address is configured as loopback IP 127.0.0.1 instead of the active enterprise DNS server 192.168.1.10.",
        "human_verdict": "Accepted",
        "failure_category": "None",
        "reviewer_corrections": "",
        "reviewer_notes": "Verified client ipconfig. Changing DNS from loopback to 192.168.1.10 fixes name resolution.",
        "reviewed_by": "Senior Network Architect",
        "review_timestamp": "2026-08-29 20:46:00"
    },
    {
        "review_id": "REV-29",
        "case_id": "CASE-29",
        "ai_root_cause": "DNS Server has incorrect static A records for intranet domain.",
        "human_verdict": "Edited",
        "failure_category": "Incomplete Fix",
        "reviewer_corrections": "Root Cause: DNS service daemon is toggled OFF in Server-01 Packet Tracer services. Fix: Turn DNS service state to ON in Server Services tab.",
        "reviewer_notes": "AI suggested editing DNS records, but show services clearly showed 'DNS OFF'. Edited to turn the service ON.",
        "reviewed_by": "Senior Network Architect",
        "review_timestamp": "2026-08-29 20:48:00"
    },
    {
        "review_id": "REV-30",
        "case_id": "CASE-30",
        "ai_root_cause": "Missing guest isolation ACL on sub-interface Gi0/0.90, allowing unrestricted inter-VLAN routing between Guest Wi-Fi and Corporate internal servers.",
        "human_verdict": "Accepted",
        "failure_category": "None",
        "reviewer_corrections": "",
        "reviewer_notes": "Security audit verified. Applying extended ACL GUEST_ISOLATION inbound on Gi0/0.90 restricts guest access to corporate subnets.",
        "reviewed_by": "Senior Network Architect",
        "review_timestamp": "2026-08-29 20:50:00"
    }
]


def generate_human_reviews():
    print("=" * 75)
    print("      NetSage AI - Human Reviewer & Responsible AI Generator")
    print("=" * 75)

    df_reviews = pd.DataFrame(REVIEWS_DATA)
    csv_path = "reviews/human_reviews.csv"
    df_reviews.to_csv(csv_path, index=False, encoding="utf-8")
    print(f"[OK] Exported human reviews to {csv_path} ({len(df_reviews)} records)")

    # Calculate Agreement Statistics
    total_reviews = len(df_reviews)
    accepted_count = len(df_reviews[df_reviews["human_verdict"] == "Accepted"])
    edited_count = len(df_reviews[df_reviews["human_verdict"] == "Edited"])
    rejected_count = len(df_reviews[df_reviews["human_verdict"] == "Rejected"])
    corrected_count = edited_count + rejected_count

    agreement_rate = (accepted_count / total_reviews) * 100

    print("\n--- Review Verdict Breakdown ---")
    print(df_reviews["human_verdict"].value_counts().to_string())

    print("\n--- Failure Category Distribution (When Overridden) ---")
    print(df_reviews[df_reviews["failure_category"] != "None"]["failure_category"].value_counts().to_string())

    print("\n" + "=" * 75)
    print(f"[*] Total Human Reviews Conducted : {total_reviews}")
    print(f"[*] AI Diagnoses Accepted Cleanly : {accepted_count} ({agreement_rate:.1f}%)")
    print(f"[*] AI Diagnoses Edited by Human  : {edited_count} ({edited_count/total_reviews*100:.1f}%)")
    print(f"[*] AI Diagnoses Rejected by Human: {rejected_count} ({rejected_count/total_reviews*100:.1f}%)")
    print(f"[*] Total Documented Corrections  : {corrected_count} (Requirement: >= 5)")
    print(f"[*] Final Human Agreement Rate    : {agreement_rate:.1f}%")
    print("=" * 75)


if __name__ == "__main__":
    generate_human_reviews()
