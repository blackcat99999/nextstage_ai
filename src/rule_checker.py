"""
NetSage AI - Deterministic Network Rule Checker
Parses Cisco IOS CLI show command outputs and topology metadata to detect
deterministic network configuration errors prior to AI reasoning.
"""

import re
import ipaddress
from typing import List, Optional, Dict, Any, Set
try:
    from src.schema import RuleFinding
except ImportError:
    from schema import RuleFinding


class DeterministicRuleChecker:
    """
    Modular deterministic network rule evaluation engine.
    Applies regex parsing, IP arithmetic, and Cisco IOS logic rules.
    """

    def __init__(self):
        pass

    def evaluate_all(self, show_outputs: str, topology_notes: str = "", symptom: str = "") -> List[RuleFinding]:
        """Runs all deterministic rules against provided evidence."""
        findings: List[RuleFinding] = []
        combined_text = f"{symptom}\n{topology_notes}\n{show_outputs}"

        # Execute all rule checkers
        findings.extend(self.check_duplicate_ips(combined_text))
        findings.extend(self.check_gateway_and_subnet_mismatch(combined_text))
        findings.extend(self.check_interface_down_status(show_outputs))
        findings.extend(self.check_vlan_database_and_assignment(show_outputs))
        findings.extend(self.check_cdp_native_vlan_mismatch(show_outputs))
        findings.extend(self.check_missing_route(show_outputs, combined_text))
        findings.extend(self.check_nat_inside_outside_pairing(show_outputs))
        findings.extend(self.check_ospf_anomalies(show_outputs))

        return findings

    # -------------------------------------------------------------------------
    # RULE 1: Duplicate IP & ARP Conflict Detection (Step 17)
    # -------------------------------------------------------------------------
    def check_duplicate_ips(self, text: str) -> List[RuleFinding]:
        findings = []
        # Pattern 1: Cisco IOS %IP-4-DUPADDR syslog
        dup_match = re.search(r"%IP-4-DUPADDR:\s*Duplicate address\s*([\d\.]+)\s*on\s*([^\s,]+)", text, re.IGNORECASE)
        if dup_match:
            ip_addr, iface = dup_match.group(1), dup_match.group(2)
            findings.append(RuleFinding(
                rule_id="RULE-01-DUP-IP",
                rule_name="Duplicate IP Address Conflict",
                severity="Critical",
                matched_text=dup_match.group(0),
                description=f"Duplicate IP address {ip_addr} detected on interface {iface}. ARP flapping occurs when two hosts claim the same IP.",
                suggested_action=f"Inspect switch MAC address table for conflicting MAC and reassign unique IP on rogue device."
            ))

        # Pattern 2: Duplicate entries in ARP output
        arp_lines = re.findall(r"Internet\s+([\d\.]+)\s+[\d\-]+\s+([0-9a-fA-F\.]{14})", text)
        ip_counts = {}
        for ip, mac in arp_lines:
            ip_counts.setdefault(ip, set()).add(mac)
        for ip, macs in ip_counts.items():
            if len(macs) > 1:
                findings.append(RuleFinding(
                    rule_id="RULE-01-DUP-IP-ARP",
                    rule_name="ARP Table Multi-MAC Conflict",
                    severity="Critical",
                    matched_text=f"IP {ip} mapped to MACs: {', '.join(macs)}",
                    description=f"IP {ip} is claimed by multiple distinct MAC addresses ({', '.join(macs)}).",
                    suggested_action=f"Isolate conflicting host port and clear ARP cache."
                ))
        return findings

    # -------------------------------------------------------------------------
    # RULE 2: Default Gateway & Subnet Mismatch Detector (Step 18)
    # -------------------------------------------------------------------------
    def check_gateway_and_subnet_mismatch(self, text: str) -> List[RuleFinding]:
        findings = []
        # Extract host IP, subnet mask, and default gateway from ipconfig / CLI
        host_ip_match = re.search(r"IP[ -]Address[.\s:]+([\d\.]+)", text, re.IGNORECASE)
        mask_match = re.search(r"Subnet Mask[.\s:]+([\d\.]+)", text, re.IGNORECASE)
        gw_match = re.search(r"Default Gateway[.\s:]+([\d\.]+)", text, re.IGNORECASE)

        if host_ip_match and gw_match:
            host_ip_str = host_ip_match.group(1).strip()
            gw_ip_str = gw_match.group(1).strip()

            # Check 1: Gateway is 0.0.0.0 or unassigned
            if gw_ip_str in ["0.0.0.0", "unset", "none"]:
                findings.append(RuleFinding(
                    rule_id="RULE-02-GW-MISSING",
                    rule_name="Missing Default Gateway",
                    severity="High",
                    matched_text=f"Default Gateway: {gw_ip_str}",
                    description=f"Host has IP {host_ip_str} but no default gateway (0.0.0.0) configured. Cannot reach remote subnets.",
                    suggested_action="Configure valid default gateway on host or add 'default-router' option to DHCP pool."
                ))
                return findings

            # Check 2: APIPA address (169.254.x.x)
            if host_ip_str.startswith("169.254."):
                findings.append(RuleFinding(
                    rule_id="RULE-02-APIPA-DETECTED",
                    rule_name="DHCP Autoconfiguration / APIPA Address",
                    severity="High",
                    matched_text=f"IP Address: {host_ip_str}",
                    description="Host is using an APIPA address (169.254.x.x), indicating DHCP lease negotiation failed.",
                    suggested_action="Verify DHCP relay (ip helper-address) on router or check DHCP pool exhaustion."
                ))
                return findings

            # Check 3: Mathematical subnet mismatch between Host and Gateway
            if mask_match:
                mask_str = mask_match.group(1).strip()
                try:
                    host_net = ipaddress.IPv4Network(f"{host_ip_str}/{mask_str}", strict=False)
                    gw_ip = ipaddress.IPv4Address(gw_ip_str)

                    if gw_ip not in host_net:
                        findings.append(RuleFinding(
                            rule_id="RULE-02-GW-SUBNET-MISMATCH",
                            rule_name="Gateway Outside Local Subnet",
                            severity="High",
                            matched_text=f"Host: {host_ip_str}/{mask_str}, Gateway: {gw_ip_str}",
                            description=f"Default gateway {gw_ip_str} does not belong to host subnet {host_net}.",
                            suggested_action=f"Correct the host gateway to an IP inside subnet {host_net} (e.g. router interface IP)."
                        ))
                except Exception:
                    pass

        # Check 4: Host gateway mismatch with known router interface IP in show output
        router_if_match = re.search(r"(?:GigabitEthernet|FastEthernet|Serial)[\d\/\.]+\s+([\d\.]+)\s+YES", text)
        if router_if_match and gw_match and host_ip_match:
            router_ip = router_if_match.group(1).strip()
            gw_ip_str = gw_match.group(1).strip()
            host_ip_str = host_ip_match.group(1).strip()
            if gw_ip_str not in ["0.0.0.0", "unset"] and router_ip != gw_ip_str and not host_ip_str.startswith("169.254."):
                # Check if router IP and host IP are in the same /24
                if router_ip.rsplit(".", 1)[0] == host_ip_str.rsplit(".", 1)[0]:
                    findings.append(RuleFinding(
                        rule_id="RULE-02-GW-TYPO",
                        rule_name="Default Gateway Typo Detected",
                        severity="High",
                        matched_text=f"Host Gateway: {gw_ip_str} vs Router Interface IP: {router_ip}",
                        description=f"Host is configured with gateway {gw_ip_str}, but router gateway on this segment is {router_ip}.",
                        suggested_action=f"Update host default gateway to {router_ip}."
                    ))

        return findings

    # ---------------------------------------------------------
    # RULE 3: Interface Status Parser (administratively down / protocol down) (Step 19)
    # ---------------------------------------------------------
    def check_interface_down_status(self, show_outputs: str) -> List[RuleFinding]:
        findings = []
        # Search for interface lines in show ip interface brief
        intf_lines = re.findall(
            r"([A-Za-z0-9\/\.\-]+)\s+([\d\.]+|unassigned)\s+YES\s+[A-Za-z]+\s+(administratively down|down|up)\s+(down|up)",
            show_outputs,
            re.IGNORECASE
        )
        for iface, ip, status, protocol in intf_lines:
            status_lower, protocol_lower = status.lower(), protocol.lower()

            if "administratively down" in status_lower:
                findings.append(RuleFinding(
                    rule_id="RULE-03-IFACE-ADMIN-DOWN",
                    rule_name="Interface Administratively Shutdown",
                    severity="High",
                    matched_text=f"{iface} is {status}, protocol is {protocol}",
                    description=f"Interface {iface} is administratively shutdown (shutdown command applied).",
                    suggested_action=f"Execute 'no shutdown' under interface {iface} configuration mode."
                ))
            elif status_lower == "up" and protocol_lower == "down":
                findings.append(RuleFinding(
                    rule_id="RULE-03-IFACE-PROTOCOL-DOWN",
                    rule_name="Interface Protocol Down (Layer 2 / Encapsulation Fault)",
                    severity="High",
                    matched_text=f"{iface} Status: up, Protocol: down",
                    description=f"Interface {iface} is physically up but Line Protocol is down. Indicates Layer 2 framing, dot1Q missing encapsulation, or keepalive failure.",
                    suggested_action=f"Verify 802.1Q encapsulation ('encapsulation dot1Q <vlan>') or clock rate/framing on {iface}."
                ))
        return findings

    # ---------------------------------------------------------
    # RULE 4: VLAN Database & Access Port Existence Checker (Step 20)
    # ---------------------------------------------------------
    def check_vlan_database_and_assignment(self, show_outputs: str) -> List[RuleFinding]:
        findings = []
        # Extract VLANs present in "show vlan brief"
        vlan_brief_match = re.search(r"VLAN Name\s+Status\s+Ports\s*\n[- ]+\n([\s\S]*?)(?:\n\n|\n[A-Z0-9\-]+#|\Z)", show_outputs)
        if vlan_brief_match:
            vlan_table_text = vlan_brief_match.group(1)
            defined_vlans = set(re.findall(r"^(\d+)\s+", vlan_table_text, re.MULTILINE))

            # Extract VLAN assignments in running config or switchport
            assigned_vlans = re.findall(r"switchport access vlan\s+(\d+)", show_outputs, re.IGNORECASE)
            assigned_vlans += re.findall(r"Access Mode VLAN:\s+(\d+)", show_outputs, re.IGNORECASE)

            for vlan_id in assigned_vlans:
                if vlan_id not in defined_vlans and vlan_id != "1":
                    findings.append(RuleFinding(
                        rule_id="RULE-04-VLAN-MISSING-DB",
                        rule_name="Assigned VLAN Not in Database",
                        severity="High",
                        matched_text=f"Port assigned to VLAN {vlan_id}, but VLAN {vlan_id} absent from 'show vlan brief'",
                        description=f"Switch ports are assigned to VLAN {vlan_id}, but VLAN {vlan_id} has not been created in the switch VLAN database.",
                        suggested_action=f"Create VLAN in global config: 'vlan {vlan_id}' -> 'name <name>' -> 'state active'."
                    ))

        # Check for trunk port in dynamic auto / static access
        dtp_access_match = re.search(r"Administrative Mode:\s*dynamic auto\s*\nOperational Mode:\s*static access", show_outputs, re.IGNORECASE)
        if dtp_access_match and "show interfaces trunk" in show_outputs:
            if "(No active trunk interfaces listed)" in show_outputs or "show interfaces trunk\n\n" in show_outputs:
                findings.append(RuleFinding(
                    rule_id="RULE-04-TRUNK-NOT-OPERATIONAL",
                    rule_name="Trunk Link Inactive / Static Access Mode",
                    severity="High",
                    matched_text=dtp_access_match.group(0),
                    description="Inter-switch link failed to negotiate 802.1Q trunking and fell back to static access mode.",
                    suggested_action="Hardcode trunk mode: 'switchport mode trunk' and 'switchport trunk allowed vlan ...'"
                ))

        return findings

    # ---------------------------------------------------------
    # RULE 5: CDP Native VLAN Mismatch (VLAN)
    # ---------------------------------------------------------
    def check_cdp_native_vlan_mismatch(self, show_outputs: str) -> List[RuleFinding]:
        findings = []
        cdp_match = re.search(
            r"%CDP-4-NATIVE_VLAN_MISMATCH:\s*Native VLAN mismatch discovered on ([^\s]+)\s*\((\d+)\),\s*with\s*([^\s]+)\s*([^\s]+)\s*\((\d+)\)",
            show_outputs,
            re.IGNORECASE
        )
        if cdp_match:
            local_if, local_vlan, remote_dev, remote_if, remote_vlan = cdp_match.groups()
            findings.append(RuleFinding(
                rule_id="RULE-05-NATIVE-VLAN-MISMATCH",
                rule_name="802.1Q Native VLAN Mismatch",
                severity="Critical",
                matched_text=cdp_match.group(0),
                description=f"Native VLAN mismatch: Local {local_if} is on Native VLAN {local_vlan}, but remote {remote_dev} {remote_if} is on Native VLAN {remote_vlan}.",
                suggested_action=f"Configure matching native VLANs: 'switchport trunk native vlan {local_vlan}' on {remote_dev}."
            ))
        return findings

    # ---------------------------------------------------------
    # RULE 5B: Missing Route & Gateway of Last Resort (Routing)
    # ---------------------------------------------------------
    def check_missing_route(self, show_outputs: str, combined_text: str = "") -> List[RuleFinding]:
        findings = []
        if "% Subnet not in table" in show_outputs or "Gateway of last resort is not set" in show_outputs:
            if "ping" in combined_text.lower() or "reach" in combined_text.lower() or "drop" in combined_text.lower():
                findings.append(RuleFinding(
                    rule_id="RULE-05-MISSING-ROUTE",
                    rule_name="Missing Route / Gateway of Last Resort Not Set",
                    severity="High",
                    matched_text="Gateway of last resort is not set / % Subnet not in table",
                    description="Router routing table lacks a destination or return route for target subnet, and no default gateway (0.0.0.0/0) is configured.",
                    suggested_action="Configure static route ('ip route <subnet> <mask> <next-hop>') or enable dynamic routing."
                ))

        # Check for invalid static next-hop outside connected interface subnet
        static_match = re.search(r"ip route ([\d\.]+) ([\d\.]+) ([\d\.]+)", show_outputs)
        intf_ip_match = re.search(r"Serial[\d\/\.]+\s+([\d\.]+)\s+YES", show_outputs)
        if static_match and intf_ip_match:
            dest_net, mask, next_hop = static_match.groups()
            local_p2p_ip = intf_ip_match.group(1)
            # If point-to-point /30 subnet (e.g. 172.16.1.1 and 172.16.1.6)
            if local_p2p_ip.rsplit(".", 1)[0] == next_hop.rsplit(".", 1)[0]:
                last_octet_local = int(local_p2p_ip.rsplit(".", 1)[1])
                last_octet_hop = int(next_hop.rsplit(".", 1)[1])
                if abs(last_octet_local - last_octet_hop) > 3:
                    findings.append(RuleFinding(
                        rule_id="RULE-05-INVALID-STATIC-NEXTHOP",
                        rule_name="Invalid Static Route Next-Hop Subnet",
                        severity="High",
                        matched_text=f"ip route {dest_net} {mask} {next_hop} on link with {local_p2p_ip}",
                        description=f"Static route next-hop {next_hop} does not reside in the connected /30 point-to-point interface subnet of {local_p2p_ip}.",
                        suggested_action=f"Change static route next-hop to the neighbor interface IP on the same /30 subnet."
                    ))
        return findings

    # ---------------------------------------------------------
    # RULE 6: NAT Inside / Outside Directive Pairing (NAT)
    # ---------------------------------------------------------
    def check_nat_inside_outside_pairing(self, show_outputs: str) -> List[RuleFinding]:
        findings = []
        if "ip nat" in show_outputs.lower():
            has_inside = "ip nat inside" in show_outputs
            has_outside = "ip nat outside" in show_outputs

            if has_inside and not has_outside:
                findings.append(RuleFinding(
                    rule_id="RULE-06-NAT-MISSING-OUTSIDE",
                    rule_name="NAT Missing Outside Interface Directive",
                    severity="Critical",
                    matched_text="ip nat inside present; missing 'ip nat outside' on WAN interface",
                    description="NAT configuration is active and 'ip nat inside' is present, but no WAN interface has 'ip nat outside'.",
                    suggested_action="Apply 'ip nat outside' to the WAN/ISP facing interface."
                ))
            elif has_outside and not has_inside:
                findings.append(RuleFinding(
                    rule_id="RULE-06-NAT-MISSING-INSIDE",
                    rule_name="NAT Missing Inside Interface Directive",
                    severity="Critical",
                    matched_text="ip nat outside present; missing 'ip nat inside' on LAN interface",
                    description="NAT configuration is active and 'ip nat outside' is present, but internal LAN interface lacks 'ip nat inside'.",
                    suggested_action="Apply 'ip nat inside' to the internal LAN interface."
                ))

            # Check for PAT overload keyword
            nat_pool_match = re.search(r"ip nat inside source list \d+ interface [^\s\n]+", show_outputs)
            if nat_pool_match and "overload" not in nat_pool_match.group(0).lower():
                findings.append(RuleFinding(
                    rule_id="RULE-06-PAT-MISSING-OVERLOAD",
                    rule_name="PAT Missing Overload Keyword",
                    severity="High",
                    matched_text=nat_pool_match.group(0),
                    description="NAT source statement lacks the 'overload' keyword, restricting translation to only 1 single simultaneous client.",
                    suggested_action="Re-enter command with 'overload' appended: 'ip nat inside source list ... overload'."
                ))
        return findings

    # ---------------------------------------------------------
    # RULE 7: OSPF Passive Interface & Wildcard Mask Inversion (Routing)
    # ---------------------------------------------------------
    def check_ospf_anomalies(self, show_outputs: str) -> List[RuleFinding]:
        findings = []
        # Check OSPF Passive on neighbor link
        if "No Hellos (Passive interface)" in show_outputs and "router ospf" in show_outputs:
            passive_match = re.search(r"passive-interface\s+([A-Za-z0-9\/\.\-]+)", show_outputs)
            iface_name = passive_match.group(1) if passive_match else "active link"
            findings.append(RuleFinding(
                rule_id="RULE-07-OSPF-PASSIVE-MISCONFIG",
                rule_name="OSPF Passive Interface on Adjacency Link",
                severity="Critical",
                matched_text=f"passive-interface {iface_name} / No Hellos (Passive interface)",
                description=f"Interface {iface_name} is configured as passive in OSPF, suppressing Hello packets and preventing neighbor adjacency.",
                suggested_action=f"Under 'router ospf <pid>', execute 'no passive-interface {iface_name}'."
            ))

        # Check OSPF Area Mismatch Syslog
        area_mismatch = re.search(r"%OSPF-4-ERRRCV:\s*Received packet with invalid area ID\s*([\d\.]+).*?area\s*([\d\.]+)", show_outputs)
        if area_mismatch:
            rcv_area, local_area = area_mismatch.group(1), area_mismatch.group(2)
            findings.append(RuleFinding(
                rule_id="RULE-07-OSPF-AREA-MISMATCH",
                rule_name="OSPF Neighbor Area ID Mismatch",
                severity="High",
                matched_text=area_mismatch.group(0),
                description=f"OSPF Area mismatch: Received Hello with Area {rcv_area} on interface configured for Area {local_area}.",
                suggested_action=f"Align OSPF network area definitions so both neighboring interfaces share the same Area ID."
            ))

        # Check OSPF Wildcard Mask Inversion (e.g. 255.255.255.0 instead of 0.0.0.255)
        ospf_net_mask_err = re.search(r"network\s+[\d\.]+\s+(255\.255\.\d+\.\d+)\s+area", show_outputs)
        if ospf_net_mask_err:
            findings.append(RuleFinding(
                rule_id="RULE-07-OSPF-WILDCARD-ERROR",
                rule_name="OSPF Wildcard Mask Inversion Error",
                severity="Medium",
                matched_text=ospf_net_mask_err.group(0),
                description=f"Subnet mask format '{ospf_net_mask_err.group(1)}' used in OSPF network command instead of inverted wildcard mask.",
                suggested_action="Use inverted wildcard mask (e.g. replace 255.255.255.0 with 0.0.0.255)."
            ))

        return findings
