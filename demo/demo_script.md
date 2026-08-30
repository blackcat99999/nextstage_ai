# NetSage AI: Official Demo Presentation & Video Script (5–10 Minutes)

**Project Title:** NetSage AI: AI-Assisted Network Troubleshooting Helper with Human Review  
**Course / Domain:** Modern AI & Cisco Networking Labs  
**Target Duration:** 8–10 Minutes  

---

## ⏱️ Timeline & Presentation Structure

| Timestamp | Section | Visual Scene / Screen Share | Key Speaker Talking Points |
| :--- | :--- | :--- | :--- |
| **0:00 – 1:30** | **Project Overview & Architecture** | Project Slide / Dashboard Architecture | Problem Statement: Junior engineers know isolated commands but struggle to connect symptoms to root causes. NetSage AI unifies deterministic Python rule checks, Tier-3 AI reasoning, and a mandatory human review gate. |
| **1:30 – 3:30** | **Broken Lab Demonstration** | Cisco Packet Tracer UI | Open broken topology. Show Student PC in VLAN 10 pinging server at 192.168.20.80 (ping works), but web browsing (HTTP port 80) fails. Run CLI commands on R1: `show access-lists 101`, `show running-config interface Gi0/0.20`. |
| **3:30 – 5:30** | **NetSage AI Diagnosis in Action** | NetSage AI Streamlit Dashboard (Live Troubleshooter) | Paste symptom and CLI outputs into NetSage AI. Click **Run Diagnostic Pipeline**. Show instant deterministic rule pre-filtering, quoted verbatim evidence (`Implicit deny ip any any`), OSI Layer 4 classification, and generated Cisco IOS remediation. |
| **5:30 – 7:00** | **Human-in-the-Loop Review Gate** | NetSage AI Human Review Interface | Walk through reviewer evaluation. Reviewer audits the proposed fix for safety (ensuring no `reload` or `erase` commands), refines the ACL rule parameters to include both HTTP (80) and HTTPS (443), and clicks **Accept & Save Review**. |
| **7:00 – 8:30** | **Applying the Fix & Verification** | Cisco Packet Tracer CLI & PC Browser | Copy approved remediation commands into Router R1 terminal. Re-run web browser on Student PC. Demonstrate instant successful HTTP web page load! Show `show access-lists 101` match counters incrementing. |
| **8:30 – 10:00** | **Analytics & Responsible AI Audit** | NetSage AI Dashboard (Analytics & Responsible AI Tabs) | Present dataset breakdown across all 30 cases (8 domains, 4 OSI layers). Highlight the **83.3% Human Agreement Rate** and review the 5 documented Responsible AI correction case studies where humans caught AI hallucinations and omissions. |

---

## 🎙️ Detailed Spoken Script

### 🎬 Part 1: Project Overview & Architecture (0:00 – 1:30)
> *"Hello everyone! Welcome to the demonstration of **NetSage AI**, an AI-assisted network troubleshooting assistant designed for enterprise campus networks and Cisco Packet Tracer environments.*
>
> *In networking, junior engineers often know individual CLI commands like `show ip route` or `show vlan brief`, but struggle to connect a complex failure symptom to the actual root cause across the OSI stack.*
>
> *NetSage AI solves this by deploying a **hybrid multi-stage pipeline**:*
> 1. *A **Deterministic Python Rule Engine** that catches mathematical subnet errors, duplicate IPs, disabled interfaces, and VLAN omissions with 100% precision.*
> 2. *A **Tier-3 AI Reasoning Specialist** that quotes verbatim CLI evidence to diagnose multi-layer protocol faults.*
> 3. *A **Cisco IOS Syntax & Safety Linter** that blocks destructive commands.*
> 4. *And most importantly, a **Mandatory Human Review Gate**, ensuring no configuration change is ever applied without engineer verification.*
> *Let’s dive into a live broken lab scenario!"*

---

### 🎬 Part 2: Broken Packet Tracer Lab Demo (1:30 – 3:30)
> *(Switch screen to Cisco Packet Tracer)*
> *"Here we have a standard campus network. Student PC `PC-01` resides in VLAN 10 on IP `192.168.10.25`. The Campus Web Server resides in VLAN 20 on IP `192.168.20.80`.*
>
> *When we open the command prompt on `PC-01` and ping `192.168.20.80`, the ping succeeds with 0% packet loss!*
> *However, when the student opens the Web Browser to `http://192.168.20.80`, the connection times out completely.*
>
> *Let's gather evidence by running show commands on Gateway Router `R1`:*
> - `R1# show ip interface brief`
> - `R1# show running-config interface GigabitEthernet0/0.20`
> - `R1# show access-lists 101`
> *Let's copy these outputs into NetSage AI."*

---

### 🎬 Part 3: NetSage AI Diagnostic Pipeline (3:30 – 5:30)
> *(Switch screen to NetSage AI Dashboard -> Live Troubleshooter)*
> *"We paste the symptom and the CLI show-outputs into NetSage AI and click **Run NetSage AI Diagnostic Pipeline**.*
>
> *Within milliseconds, NetSage AI provides a structured diagnosis:*
> - **Inferred Root Cause:** `ACL 101 permits only ICMP traffic; HTTP (TCP port 80) and HTTPS (TCP port 443) traffic is blocked by the implicit deny ip any any at the end of the ACL.`
> - **Target OSI Layer:** `Layer 4 (Transport)` with `High` confidence.
> - **Verbatim Evidence:** `(Implicit deny ip any any active at end)`.
> - **Cisco IOS Remediation Sequence:** Generating precise `permit tcp ... eq 80` rules.*
>
> *The built-in syntax linter also awards a 100/100 safety score, confirming no destructive commands were generated."*

---

### 🎬 Part 4: Human-in-the-Loop Review Gate (5:30 – 7:00)
> *"Now comes our core safety pillar: **Human Oversight**.*
> *As senior network engineers, we examine the AI's diagnosis. We confirm the ACL logic is accurate, but we also want to ensure both HTTP port 80 and HTTPS port 443 are permitted.*
>
> *We add our engineering reviewer notes: 'Approved - verified ACL 101 omission on sub-interface Gi0/0.20', select the **Accepted** verdict, and click **Submit & Save Human Review Log**.*
> *The feedback is logged live to our audit records."*

---

### 🎬 Part 5: Applying the Fix & Verification (7:00 – 8:30)
> *(Switch back to Cisco Packet Tracer)*
> *"Now we paste the approved Cisco IOS remediation commands into Router `R1`:*
> ```cisco
> R1# configure terminal
> R1(config)# ip access-list extended 101
> R1(config-ext-nacl)# 20 permit tcp 192.168.10.0 0.0.0.255 host 192.168.20.80 eq 80
> R1(config-ext-nacl)# 30 permit tcp 192.168.10.0 0.0.0.255 host 192.168.20.80 eq 443
> R1(config-ext-nacl)# end
> ```
> *Let's test again from `PC-01`.*
> *We open the browser to `http://192.168.20.80`... and boom! **'Welcome to Campus Portal'** loads instantly!*
> *Running `show access-lists 101` on R1 shows match counters incrementing on line 20. The network is 100% restored!"*

---

### 🎬 Part 6: Analytics Dashboard & Responsible AI Audit (8:30 – 10:00)
> *(Switch back to Dashboard -> Analytics & Responsible AI Tabs)*
> *"Finally, let's explore our complete project analytics:*
> - *Our benchmark dataset covers **30 complete cases** across 8 domains (VLAN, DHCP, Gateway, Routing, ACL, NAT, Wireless, and DNS).*
> - *Our **Deterministic Rule Checker** handles 50% of common errors instantly.*
> - *Across human review, NetSage AI achieved an **83.3% Human Agreement Rate**.*
> - *In our **Responsible AI Audit Log**, we thoroughly analyzed **5 case studies** where human engineers corrected AI hallucinations, incomplete pool exclusions, and unsafe reload suggestions.*
>
> *NetSage AI demonstrates how pairing deterministic rules, structured AI reasoning, and strict human review creates a reliable, safety-first network automation tool. Thank you!"*
