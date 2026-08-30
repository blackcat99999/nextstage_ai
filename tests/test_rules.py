"""
NetSage AI - Deterministic Rule Checker Unit Tests
Validates all deterministic checks against synthetic and dataset Cisco CLI outputs.
"""

import pytest
import sys
import os

# Add root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.rule_checker import DeterministicRuleChecker
from src.schema import RuleFinding


@pytest.fixture
def checker():
    return DeterministicRuleChecker()


def test_duplicate_ip_rule(checker):
    sample_text = """
    %IP-4-DUPADDR: Duplicate address 192.168.100.1 on GigabitEthernet0/1, sourced by 0001.9654.abcd
    """
    findings = checker.check_duplicate_ips(sample_text)
    assert len(findings) > 0
    assert findings[0].rule_id == "RULE-01-DUP-IP"
    assert findings[0].severity == "Critical"
    assert "192.168.100.1" in findings[0].description


def test_gateway_mismatch_rule(checker):
    sample_text = """
    PC-HQ> ipconfig
    FastEthernet0 Connection:
       IP Address......................: 192.168.1.45
       Subnet Mask.....................: 255.255.255.0
       Default Gateway.................: 192.168.1.254

    Router# show ip interface brief
    GigabitEthernet0/0         192.168.1.1     YES manual up                    up
    """
    findings = checker.check_gateway_and_subnet_mismatch(sample_text)
    assert len(findings) > 0
    rule_ids = [f.rule_id for f in findings]
    assert "RULE-02-GW-TYPO" in rule_ids


def test_apipa_rule(checker):
    sample_text = """
    Client-PC# ipconfig
    IP Address. . . . . . . . . . . . : 169.254.42.88
    Subnet Mask . . . . . . . . . . . : 255.255.0.0
    Default Gateway . . . . . . . . . : 0.0.0.0
    """
    findings = checker.check_gateway_and_subnet_mismatch(sample_text)
    assert len(findings) > 0
    rule_ids = [f.rule_id for f in findings]
    assert "RULE-02-APIPA-DETECTED" in rule_ids or "RULE-02-GW-MISSING" in rule_ids


def test_interface_down_rule(checker):
    sample_text = """
    R1# show ip interface brief
    Interface              IP-Address      OK? Method Status                Protocol
    GigabitEthernet0/0/0   unassigned      YES unset  up                    up
    GigabitEthernet0/0/0.30 192.168.30.1   YES manual up                    down
    """
    findings = checker.check_interface_down_status(sample_text)
    assert len(findings) > 0
    assert findings[0].rule_id == "RULE-03-IFACE-PROTOCOL-DOWN"


def test_missing_vlan_database_rule(checker):
    sample_text = """
    SW-Floor2# show running-config interface FastEthernet0/11
    interface FastEthernet0/11
     switchport access vlan 40
     switchport mode access
    !
    SW-Floor2# show vlan brief
    VLAN Name                             Status    Ports
    ---- -------------------------------- --------- -------------------------------
    1    default                          active    Fa0/1, Fa0/2
    10   Data                             active    Fa0/5, Fa0/6
    """
    findings = checker.check_vlan_database_and_assignment(sample_text)
    assert len(findings) > 0
    assert findings[0].rule_id == "RULE-04-VLAN-MISSING-DB"


def test_cdp_native_vlan_mismatch_rule(checker):
    sample_text = """
    %CDP-4-NATIVE_VLAN_MISMATCH: Native VLAN mismatch discovered on GigabitEthernet0/1 (99), with SW-Dist1 GigabitEthernet0/1 (1).
    """
    findings = checker.check_cdp_native_vlan_mismatch(sample_text)
    assert len(findings) > 0
    assert findings[0].rule_id == "RULE-05-NATIVE-VLAN-MISMATCH"


def test_nat_missing_outside_rule(checker):
    sample_text = """
    interface GigabitEthernet0/0
     ip address 192.168.1.1 255.255.255.0
     ip nat inside
    !
    interface GigabitEthernet0/1
     ip address 203.0.113.2 255.255.255.252
    !
    """
    findings = checker.check_nat_inside_outside_pairing(sample_text)
    assert len(findings) > 0
    assert findings[0].rule_id == "RULE-06-NAT-MISSING-OUTSIDE"


def test_ospf_passive_rule(checker):
    sample_text = """
    R1# show ip ospf interface GigabitEthernet0/1
    GigabitEthernet0/1 is up, line protocol is up
      Internet Address 10.1.1.1/30, Area 0
      No Hellos (Passive interface)

    R1# show running-config | section router ospf
    router ospf 1
     passive-interface GigabitEthernet0/1
    """
    findings = checker.check_ospf_anomalies(sample_text)
    assert len(findings) > 0
    assert findings[0].rule_id == "RULE-07-OSPF-PASSIVE-MISCONFIG"


def test_missing_route_rule(checker):
    sample_text = """
    HQ-Core# show ip route 192.168.70.0
    % Subnet not in table

    HQ-Core# show ip route
    Gateway of last resort is not set
    """
    findings = checker.check_missing_route(sample_text, combined_text="ping fails and drops")
    assert len(findings) > 0
    assert findings[0].rule_id == "RULE-05-MISSING-ROUTE"


def test_invalid_static_nexthop_rule(checker):
    sample_text = """
    R-BR1# show ip interface brief Serial0/0/0
    Serial0/0/0            172.16.1.1      YES manual up                    up

    R-BR1# show running-config | include ip route
    ip route 10.0.0.0 255.0.0.0 172.16.1.6
    """
    findings = checker.check_missing_route(sample_text)
    assert len(findings) > 0
    assert findings[0].rule_id == "RULE-05-INVALID-STATIC-NEXTHOP"
