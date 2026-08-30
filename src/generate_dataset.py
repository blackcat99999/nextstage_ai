"""
NetSage AI - Dataset Generator for 30 Packet Tracer Troubleshooting Cases
Builds comprehensive, realistic Cisco CLI show command outputs, topology notes, faults, and fixes.
"""

import json
import pandas as pd
try:
    from src.schema import NetworkCase
except ImportError:
    from schema import NetworkCase

CASES: List[NetworkCase] = [
    # ---------------------------------------------------------
    # PHASE 2A: VLAN & TRUNKING (Cases 1 - 5)
    # ---------------------------------------------------------
    NetworkCase(
        case_id="CASE-01",
        domain="VLAN",
        concept_tag="Access Port VLAN Assignment",
        osi_layer="Layer 2",
        severity="High",
        symptom="PC-Sales-1 in Engineering wing cannot reach Accounting Server at 192.168.10.100. Local gateway ping fails.",
        topology_notes="Switch SW-Floor1 (WS-C2960-24TT). PC-Sales-1 on Fa0/5 (expected VLAN 10, Sales, 192.168.10.0/24). Server on VLAN 10.",
        show_outputs="""SW-Floor1# show vlan brief
VLAN Name                             Status    Ports
---- -------------------------------- --------- -------------------------------
1    default                          active    Fa0/1, Fa0/2, Fa0/3, Fa0/4
10   Sales                            active    Fa0/6, Fa0/7, Fa0/8
20   Guest                            active    Fa0/5, Fa0/9, Fa0/10
99   Management                       active    

SW-Floor1# show interfaces FastEthernet0/5 switchport
Name: Fa0/5
Switchport: Enabled
Administrative Mode: static access
Operational Mode: static access
Administrative Trunking Encapsulation: dot1q
Operational Trunking Encapsulation: native
Negotiation of Trunking: Off
Access Mode VLAN: 20 (Guest)
Trunking Native Mode VLAN: 1 (default)""",
        ground_truth_fault="Interface FastEthernet0/5 is improperly assigned to VLAN 20 (Guest) instead of VLAN 10 (Sales).",
        ground_truth_fix="""SW-Floor1# configure terminal
SW-Floor1(config)# interface FastEthernet0/5
SW-Floor1(config-if)# switchport mode access
SW-Floor1(config-if)# switchport access vlan 10
SW-Floor1(config-if)# no shutdown
SW-Floor1(config-if)# end
SW-Floor1# copy running-config startup-config"""
    ),
    NetworkCase(
        case_id="CASE-02",
        domain="VLAN",
        concept_tag="Native VLAN Mismatch",
        osi_layer="Layer 2",
        severity="Critical",
        symptom="CDP native VLAN mismatch warnings flooding console; inter-switch management traffic is dropping packets.",
        topology_notes="Trunk link between SW-Core1 (Gig0/1) and SW-Dist1 (Gig0/1). SW-Core1 uses Native VLAN 99. SW-Dist1 uses Native VLAN 1.",
        show_outputs="""%CDP-4-NATIVE_VLAN_MISMATCH: Native VLAN mismatch discovered on GigabitEthernet0/1 (99), with SW-Dist1 GigabitEthernet0/1 (1).

SW-Core1# show interfaces GigabitEthernet0/1 switchport
Name: Gi0/1
Switchport: Enabled
Administrative Mode: trunk
Operational Mode: trunk
Administrative Trunking Encapsulation: dot1q
Operational Trunking Encapsulation: dot1q
Access Mode VLAN: 1 (default)
Trunking Native Mode VLAN: 99 (Management)
Administrative Native VLAN tagging: disabled
Operational Native VLAN tagging: disabled

SW-Dist1# show interfaces GigabitEthernet0/1 switchport
Name: Gi0/1
Switchport: Enabled
Administrative Mode: trunk
Operational Mode: trunk
Administrative Trunking Encapsulation: dot1q
Operational Trunking Encapsulation: dot1q
Access Mode VLAN: 1 (default)
Trunking Native Mode VLAN: 1 (default)""",
        ground_truth_fault="Native VLAN mismatch on 802.1Q trunk link Gi0/1: SW-Core1 is configured with Native VLAN 99, while SW-Dist1 is on default Native VLAN 1.",
        ground_truth_fix="""SW-Dist1# configure terminal
SW-Dist1(config)# interface GigabitEthernet0/1
SW-Dist1(config-if)# switchport trunk native vlan 99
SW-Dist1(config-if)# end
SW-Dist1# copy running-config startup-config"""
    ),
    NetworkCase(
        case_id="CASE-03",
        domain="VLAN",
        concept_tag="Missing Trunk Mode Configuration",
        osi_layer="Layer 2",
        severity="High",
        symptom="VLAN 20 and VLAN 30 hosts on Access Switch SW-2 cannot communicate with Default Gateway located on Core Switch SW-1.",
        topology_notes="Inter-switch link between SW-1 (Gig0/1) and SW-2 (Gig0/1). SW-1 is set to trunk; SW-2 is left on default dynamic auto/access mode.",
        show_outputs="""SW-2# show interfaces GigabitEthernet0/1 switchport
Name: Gi0/1
Switchport: Enabled
Administrative Mode: dynamic auto
Operational Mode: static access
Administrative Trunking Encapsulation: dot1q
Operational Trunking Encapsulation: native
Negotiation of Trunking: On
Access Mode VLAN: 1 (default)
Trunking Native Mode VLAN: 1 (default)
Administrative Native VLAN tagging: disabled
Operational Native VLAN tagging: disabled

SW-2# show interfaces trunk
(No active trunk interfaces listed)""",
        ground_truth_fault="Uplink interface GigabitEthernet0/1 on SW-2 is operating in static access mode because DTP failed or administrative mode was not hardcoded to trunk.",
        ground_truth_fix="""SW-2# configure terminal
SW-2(config)# interface GigabitEthernet0/1
SW-2(config-if)# switchport trunk encapsulation dot1q
SW-2(config-if)# switchport mode trunk
SW-2(config-if)# switchport trunk allowed vlan 10,20,30,99
SW-2(config-if)# no shutdown
SW-2(config-if)# end"""
    ),
    NetworkCase(
        case_id="CASE-04",
        domain="VLAN",
        concept_tag="Router-on-a-Stick Dot1Q Encapsulation",
        osi_layer="Layer 3",
        severity="Critical",
        symptom="Hosts in VLAN 30 (192.168.30.0/24) cannot reach default gateway 192.168.30.1 on Router R1. VLAN 10 and 20 work fine.",
        topology_notes="Router R1 connected via GigabitEthernet0/0/0 to trunk port on Switch SW-1. Sub-interfaces Gi0/0/0.10, Gi0/0/0.20, and Gi0/0/0.30.",
        show_outputs="""R1# show ip interface brief
Interface              IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0/0   unassigned      YES unset  up                    up
GigabitEthernet0/0/0.10 192.168.10.1   YES manual up                    up
GigabitEthernet0/0/0.20 192.168.20.1   YES manual up                    up
GigabitEthernet0/0/0.30 192.168.30.1   YES manual up                    down

R1# show running-config interface GigabitEthernet0/0/0.30
Building configuration...
Current configuration : 89 bytes
!
interface GigabitEthernet0/0/0.30
 ip address 192.168.30.1 255.255.255.0
!
end""",
        ground_truth_fault="Sub-interface GigabitEthernet0/0/0.30 is missing IEEE 802.1Q encapsulation ('encapsulation dot1Q 30'), leaving the protocol status down.",
        ground_truth_fix="""R1# configure terminal
R1(config)# interface GigabitEthernet0/0/0.30
R1(config-subif)# encapsulation dot1Q 30
R1(config-subif)# ip address 192.168.30.1 255.255.255.0
R1(config-subif)# no shutdown
R1(config-subif)# end"""
    ),
    NetworkCase(
        case_id="CASE-05",
        domain="VLAN",
        concept_tag="Missing VLAN in Database",
        osi_layer="Layer 2",
        severity="Medium",
        symptom="Users connected to switch ports configured for VLAN 40 (Voice) get no link layer connectivity and traffic is blackholed.",
        topology_notes="Switch SW-Floor2. Ports Fa0/11-15 configured for 'switchport access vlan 40'.",
        show_outputs="""SW-Floor2# show running-config interface FastEthernet0/11
interface FastEthernet0/11
 switchport access vlan 40
 switchport mode access
!

SW-Floor2# show vlan brief
VLAN Name                             Status    Ports
---- -------------------------------- --------- -------------------------------
1    default                          active    Fa0/1, Fa0/2, Fa0/3, Fa0/4
10   Data                             active    Fa0/5, Fa0/6, Fa0/7, Fa0/8
20   Voice-Old                        active    Fa0/9, Fa0/10
99   Management                       active    
(VLAN 40 is missing from the VLAN database)""",
        ground_truth_fault="VLAN 40 has not been created in the local switch VLAN database, causing all ports assigned to VLAN 40 to remain inactive.",
        ground_truth_fix="""SW-Floor2# configure terminal
SW-Floor2(config)# vlan 40
SW-Floor2(config-vlan)# name Voice
SW-Floor2(config-vlan)# state active
SW-Floor2(config-vlan)# end"""
    ),

    # ---------------------------------------------------------
    # PHASE 2B: DHCP & GATEWAY (Cases 6 - 10)
    # ---------------------------------------------------------
    NetworkCase(
        case_id="CASE-06",
        domain="DHCP",
        concept_tag="Missing IP Helper Address",
        osi_layer="Layer 3",
        severity="High",
        symptom="Clients in VLAN 20 receive APIPA addresses (169.254.x.x) and cannot lease an IP address from centralized DHCP Server at 192.168.10.50.",
        topology_notes="Router R1 acts as default gateway for VLAN 10 (Gi0/0.10) and VLAN 20 (Gi0/0.20). Central DHCP server resides in VLAN 10.",
        show_outputs="""R1# show running-config interface GigabitEthernet0/0.20
Building configuration...
Current configuration : 110 bytes
!
interface GigabitEthernet0/0.20
 encapsulation dot1Q 20
 ip address 192.168.20.1 255.255.255.0
!
end

Client-PC# ipconfig
Ethernet adapter Local Area Connection:
   Connection-specific DNS Suffix  . : 
   IP Address. . . . . . . . . . . . : 169.254.42.88
   Subnet Mask . . . . . . . . . . . : 255.255.0.0
   Default Gateway . . . . . . . . . : 0.0.0.0""",
        ground_truth_fault="Router sub-interface Gi0/0.20 lacks the 'ip helper-address 192.168.10.50' configuration required to relay DHCP broadcast requests to the DHCP server.",
        ground_truth_fix="""R1# configure terminal
R1(config)# interface GigabitEthernet0/0.20
R1(config-subif)# ip helper-address 192.168.10.50
R1(config-subif)# end"""
    ),
    NetworkCase(
        case_id="CASE-07",
        domain="DHCP",
        concept_tag="DHCP Pool Scope Exclusion & Exhaustion",
        osi_layer="Layer 7",
        severity="Medium",
        symptom="New branch office workstations cannot obtain DHCP leases. Existing workstations retain current leases.",
        topology_notes="Branch Router R-Branch acts as local DHCP server for 192.168.50.0/24 subnet.",
        show_outputs="""R-Branch# show ip dhcp pool
Pool POOL_BRANCH :
 Utilization mark (high/low)    : 100 / 0
 Subnet size (total/usable)     : 254 / 5
 Total addresses                : 254
 Leased addresses               : 5
 Excluded addresses             : 249
 Pending event                  : none

R-Branch# show running-config | include ip dhcp excluded-address
ip dhcp excluded-address 192.168.50.1 192.168.50.250""",
        ground_truth_fault="DHCP excluded address range is overly broad (192.168.50.1 to 192.168.50.250), leaving only 4 usable IP addresses in the pool.",
        ground_truth_fix="""R-Branch# configure terminal
R-Branch(config)# no ip dhcp excluded-address 192.168.50.1 192.168.50.250
R-Branch(config)# ip dhcp excluded-address 192.168.50.1 192.168.50.20
R-Branch(config)# end"""
    ),
    NetworkCase(
        case_id="CASE-08",
        domain="Gateway",
        concept_tag="Default Gateway Typo",
        osi_layer="Layer 3",
        severity="High",
        symptom="Static workstation PC-HQ can ping local peers on 192.168.1.0/24 but fails to reach any external server or internet IP.",
        topology_notes="Subnet: 192.168.1.0/24. Router Gateway IP: 192.168.1.1. Host: PC-HQ.",
        show_outputs="""PC-HQ> ipconfig
FastEthernet0 Connection:
   IP Address......................: 192.168.1.45
   Subnet Mask.....................: 255.255.255.0
   Default Gateway.................: 192.168.1.254

Router# show ip interface brief | include GigabitEthernet0/0
GigabitEthernet0/0         192.168.1.1     YES manual up                    up""",
        ground_truth_fault="Workstation default gateway is misconfigured as 192.168.1.254 instead of the actual router gateway IP 192.168.1.1.",
        ground_truth_fix="""PC-HQ> ipconfig /setgateway 192.168.1.1
(Or in Packet Tracer GUI: Desktop -> IP Configuration -> Default Gateway: 192.168.1.1)"""
    ),
    NetworkCase(
        case_id="CASE-09",
        domain="DHCP",
        concept_tag="Missing Default-Router Option",
        osi_layer="Layer 7",
        severity="High",
        symptom="DHCP clients in VLAN 10 acquire valid IP address and subnet mask, but cannot access destinations outside their local subnet.",
        topology_notes="Cisco IOS Router R1 configured as DHCP Server for LAN 192.168.10.0/24. Gateway is 192.168.10.1.",
        show_outputs="""R1# show running-config | section ip dhcp pool
ip dhcp pool LAN_VLAN10
 network 192.168.10.0 255.255.255.0
 dns-server 8.8.8.8
 domain-name enterprise.local

PC-Client> ipconfig
FastEthernet0 Connection:
   IP Address......................: 192.168.10.25
   Subnet Mask.....................: 255.255.255.0
   Default Gateway.................: 0.0.0.0""",
        ground_truth_fault="DHCP pool 'LAN_VLAN10' is missing the 'default-router 192.168.10.1' configuration parameter, causing clients to have no default gateway.",
        ground_truth_fix="""R1# configure terminal
R1(config)# ip dhcp pool LAN_VLAN10
R1(config-dhcp)# default-router 192.168.10.1
R1(config-dhcp)# end"""
    ),
    NetworkCase(
        case_id="CASE-10",
        domain="Gateway",
        concept_tag="Duplicate IP / Gateway Conflict",
        osi_layer="Layer 3",
        severity="Critical",
        symptom="Intermittent gateway reachability and ARP flapping observed across all workstations in the Finance department.",
        topology_notes="Router R1 Gi0/1 has IP 192.168.100.1. A misconfigured rogue printer was statically assigned 192.168.100.1.",
        show_outputs="""R1# show ip interface brief GigabitEthernet0/1
Interface              IP-Address      OK? Method Status                Protocol
GigabitEthernet0/1     192.168.100.1   YES manual up                    up

%IP-4-DUPADDR: Duplicate address 192.168.100.1 on GigabitEthernet0/1, sourced by 0001.9654.abcd

R1# show arp | include 192.168.100.1
Internet  192.168.100.1           -   0000.0c07.ac01  ARPA   GigabitEthernet0/1
Internet  192.168.100.1           0   0001.9654.abcd  ARPA   GigabitEthernet0/1""",
        ground_truth_fault="IP address conflict: A rogue host with MAC 0001.9654.abcd has been statically assigned 192.168.100.1, conflicting with the default router gateway.",
        ground_truth_fix="""1. Identify port for MAC 0001.9654.abcd on switch: 'show mac address-table address 0001.9654.abcd'
2. Reconfigure or change host IP on rogue endpoint to an unused IP (e.g., 192.168.100.250).
3. Clear ARP cache on router: 'clear arp-cache'"""
    ),

    # ---------------------------------------------------------
    # PHASE 2C: IP ROUTING (OSPF & STATIC) (Cases 11 - 15)
    # ---------------------------------------------------------
    NetworkCase(
        case_id="CASE-11",
        domain="Routing",
        concept_tag="Invalid Static Route Next-Hop",
        osi_layer="Layer 3",
        severity="High",
        symptom="Branch router R-BR1 cannot route remote branch traffic to HQ subnet 10.0.0.0/8. Pings drop with 'Destination host unreachable'.",
        topology_notes="R-BR1 connected to ISP/HQ Router R-HQ via Serial0/0/0 (172.16.1.0/30). R-HQ Serial IP is 172.16.1.2.",
        show_outputs="""R-BR1# show ip interface brief Serial0/0/0
Interface              IP-Address      OK? Method Status                Protocol
Serial0/0/0            172.16.1.1      YES manual up                    up

R-BR1# show ip route static
Codes: S - static
S    10.0.0.0/8 [1/0] via 172.16.1.6

R-BR1# show running-config | include ip route
ip route 10.0.0.0 255.0.0.0 172.16.1.6""",
        ground_truth_fault="Static route points to 172.16.1.6, which is an invalid next-hop outside the /30 point-to-point subnet (172.16.1.0/30 allows only .1 and .2).",
        ground_truth_fix="""R-BR1# configure terminal
R-BR1(config)# no ip route 10.0.0.0 255.0.0.0 172.16.1.6
R-BR1(config)# ip route 10.0.0.0 255.0.0.0 172.16.1.2
R-BR1(config)# end"""
    ),
    NetworkCase(
        case_id="CASE-12",
        domain="Routing",
        concept_tag="OSPF Passive Interface Misconfiguration",
        osi_layer="Layer 3",
        severity="Critical",
        symptom="OSPF adjacency fails to form between Core Router R1 and Distribution Router R2 across GigabitEthernet0/1.",
        topology_notes="R1 Gi0/1 (10.1.1.1/30) <---> R2 Gi0/1 (10.1.1.2/30). Both routers running OSPF process 1.",
        show_outputs="""R1# show ip ospf neighbor
(No OSPF neighbors listed)

R1# show ip ospf interface GigabitEthernet0/1
GigabitEthernet0/1 is up, line protocol is up
  Internet Address 10.1.1.1/30, Area 0
  Process ID 1, Router ID 1.1.1.1, Network Type BROADCAST, Cost: 1
  No Hellos (Passive interface)

R1# show running-config | section router ospf
router ospf 1
 router-id 1.1.1.1
 passive-interface GigabitEthernet0/1
 network 10.1.1.0 0.0.0.3 area 0""",
        ground_truth_fault="GigabitEthernet0/1 on R1 is mistakenly configured as a passive interface ('passive-interface GigabitEthernet0/1'), preventing OSPF Hello packet exchange.",
        ground_truth_fix="""R1# configure terminal
R1(config)# router ospf 1
R1(config-router)# no passive-interface GigabitEthernet0/1
R1(config-router)# end"""
    ),
    NetworkCase(
        case_id="CASE-13",
        domain="Routing",
        concept_tag="OSPF Area Mismatch",
        osi_layer="Layer 3",
        severity="High",
        symptom="OSPF adjacency stuck in INIT/DOWN state between Router R1 and Router R2 on link 192.168.12.0/30.",
        topology_notes="Link 192.168.12.0/30 between R1 (Gi0/0) and R2 (Gi0/0).",
        show_outputs="""R1# show ip ospf interface GigabitEthernet0/0
GigabitEthernet0/0 is up, line protocol is up
  Internet Address 192.168.12.1/30, Area 0
  Process ID 1, Router ID 192.168.1.1

R2# show ip ospf interface GigabitEthernet0/0
GigabitEthernet0/0 is up, line protocol is up
  Internet Address 192.168.12.2/30, Area 1
  Process ID 1, Router ID 192.168.2.1

R1# show log
%OSPF-4-ERRRCV: Received packet with invalid area ID 0.0.0.1 from 192.168.12.2 on GigabitEthernet0/0 area 0.0.0.0""",
        ground_truth_fault="OSPF Area ID mismatch on connecting link: R1 interface is in Area 0 while R2 interface is in Area 1.",
        ground_truth_fix="""R2# configure terminal
R2(config)# router ospf 1
R2(config-router)# no network 192.168.12.0 0.0.0.3 area 1
R2(config-router)# network 192.168.12.0 0.0.0.3 area 0
R2(config-router)# end"""
    ),
    NetworkCase(
        case_id="CASE-14",
        domain="Routing",
        concept_tag="OSPF Wildcard Mask Error",
        osi_layer="Layer 3",
        severity="Medium",
        symptom="Subnet 172.16.20.0/24 on Router R1 is not being advertised to OSPF neighbors.",
        topology_notes="R1 has interface Gi0/2 configured with IP 172.16.20.1 255.255.255.0. OSPF 10.",
        show_outputs="""R1# show ip interface brief GigabitEthernet0/2
GigabitEthernet0/2         172.16.20.1     YES manual up                    up

R1# show running-config | section router ospf
router ospf 10
 router-id 1.1.1.1
 network 172.16.20.0 255.255.255.0 area 0
 network 10.0.0.0 0.0.0.3 area 0

R1# show ip ospf interface brief
Interface    PID   Area            IP Address/Mask    Cost  State Nbrs F/C
Gi0/0        10    0               10.0.0.1/30        1     P2P   1/1""",
        ground_truth_fault="Subnet mask '255.255.255.0' was entered instead of inverted wildcard mask '0.0.0.255' in the OSPF network statement, so Gi0/2 was never enabled for OSPF.",
        ground_truth_fix="""R1# configure terminal
R1(config)# router ospf 10
R1(config-router)# no network 172.16.20.0 255.255.255.0 area 0
R1(config-router)# network 172.16.20.0 0.0.0.255 area 0
R1(config-router)# end"""
    ),
    NetworkCase(
        case_id="CASE-15",
        domain="Routing",
        concept_tag="Missing Return Route / Asymmetric Routing",
        osi_layer="Layer 3",
        severity="Critical",
        symptom="Clients in Branch Subnet 192.168.70.0/24 can send packets to HQ Server 10.10.10.50, but receive no reply.",
        topology_notes="Branch Gateway BR-GW (192.168.70.1) -> WAN -> HQ-Core (10.10.10.1). HQ-Core has no route back to 192.168.70.0/24.",
        show_outputs="""HQ-Core# show ip route 192.168.70.0
% Subnet not in table

HQ-Core# show ip route
Codes: C - connected, S - static, R - RIP, O - OSPF
Gateway of last resort is not set

      10.0.0.0/8 is variably subnetted, 2 subnets, 2 masks
C        10.10.10.0/24 is directly connected, GigabitEthernet0/0
C        172.16.0.0/30 is directly connected, Serial0/0/0""",
        ground_truth_fault="HQ-Core router lacks a return route for the branch subnet 192.168.70.0/24, causing return packets to be dropped.",
        ground_truth_fix="""HQ-Core# configure terminal
HQ-Core(config)# ip route 192.168.70.0 255.255.255.0 172.16.0.2
HQ-Core(config)# end"""
    ),

    # ---------------------------------------------------------
    # PHASE 2D: ACCESS CONTROL LISTS (ACL) (Cases 16 - 20)
    # ---------------------------------------------------------
    NetworkCase(
        case_id="CASE-16",
        domain="ACL",
        concept_tag="Implicit Deny All Blocking HTTP",
        osi_layer="Layer 4",
        severity="High",
        symptom="Engineering workstations in 192.168.10.0/24 cannot browse Web Server at 192.168.20.80. ICMP ping works.",
        topology_notes="Router R1 interface Gi0/1 (facing Server farm) has inbound/outbound ACL 101 applied.",
        show_outputs="""R1# show access-lists 101
Extended IP access list 101
    10 permit icmp 192.168.10.0 0.0.0.255 192.168.20.0 0.0.0.255 (24 matches)
    (Implicit deny ip any any active at end)

R1# show running-config interface GigabitEthernet0/1
interface GigabitEthernet0/1
 ip address 192.168.20.1 255.255.255.0
 ip access-group 101 out""",
        ground_truth_fault="ACL 101 permits only ICMP traffic; HTTP (TCP port 80) and HTTPS (TCP port 443) traffic is blocked by the implicit 'deny ip any any' at the end of the ACL.",
        ground_truth_fix="""R1# configure terminal
R1(config)# ip access-list extended 101
R1(config-ext-nacl)# 20 permit tcp 192.168.10.0 0.0.0.255 host 192.168.20.80 eq 80
R1(config-ext-nacl)# 30 permit tcp 192.168.10.0 0.0.0.255 host 192.168.20.80 eq 443
R1(config-ext-nacl)# end"""
    ),
    NetworkCase(
        case_id="CASE-17",
        domain="ACL",
        concept_tag="ACL Direction Misapplication (In vs Out)",
        osi_layer="Layer 3",
        severity="High",
        symptom="ACL intended to protect Internal DB from external network is blocking internal DB requests instead.",
        topology_notes="Router Gateway R-Edge. Interface Gi0/0 is internal (10.0.0.1/24), Gi0/1 is external (203.0.113.1/30).",
        show_outputs="""R-Edge# show running-config interface GigabitEthernet0/0
interface GigabitEthernet0/0
 ip address 10.0.0.1 255.255.255.0
 ip access-group FILTER_EXT_IN in

R-Edge# show ip access-lists FILTER_EXT_IN
Extended IP access list FILTER_EXT_IN
    10 deny ip host 203.0.113.50 10.0.0.0 0.0.0.255
    20 permit ip any any (0 matches)""",
        ground_truth_fault="Access list FILTER_EXT_IN was applied as 'in' on internal interface Gi0/0 instead of 'in' on external WAN interface Gi0/1.",
        ground_truth_fix="""R-Edge# configure terminal
R-Edge(config)# interface GigabitEthernet0/0
R-Edge(config-if)# no ip access-group FILTER_EXT_IN in
R-Edge(config)# interface GigabitEthernet0/1
R-Edge(config-if)# ip access-group FILTER_EXT_IN in
R-Edge(config-if)# end"""
    ),
    NetworkCase(
        case_id="CASE-18",
        domain="ACL",
        concept_tag="ACL Port Matching Reversal (Source vs Destination)",
        osi_layer="Layer 4",
        severity="Medium",
        symptom="Clients cannot connect to Web Server port 80 through perimeter firewall router.",
        topology_notes="Router R1 filtering traffic from 192.168.1.0/24 to Web Server 172.16.1.10.",
        show_outputs="""R1# show access-lists 105
Extended IP access list 105
    10 permit tcp 192.168.1.0 0.0.0.255 eq 80 host 172.16.1.10
    (0 matches)""",
        ground_truth_fault="Port specification 'eq 80' was applied to the source port (client random ephemeral port) instead of the destination port.",
        ground_truth_fix="""R1# configure terminal
R1(config)# ip access-list extended 105
R1(config-ext-nacl)# no 10
R1(config-ext-nacl)# 10 permit tcp 192.168.1.0 0.0.0.255 host 172.16.1.10 eq 80
R1(config-ext-nacl)# end"""
    ),
    NetworkCase(
        case_id="CASE-19",
        domain="ACL",
        concept_tag="Standard ACL Placement Flaw",
        osi_layer="Layer 3",
        severity="Critical",
        symptom="Standard ACL designed to block Host A from accessing Server B inadvertently blocked Host A from accessing the entire enterprise network.",
        topology_notes="Host A (192.168.1.50) on Router R1 LAN. Server B (10.0.0.100) on remote Router R2. Standard ACL 10 applied inbound on R1 Gi0/0.",
        show_outputs="""R1# show running-config interface GigabitEthernet0/0
interface GigabitEthernet0/0
 ip address 192.168.1.1 255.255.255.0
 ip access-group 10 in

R1# show access-lists 10
Standard IP access list 10
    10 deny 192.168.1.50
    20 permit any""",
        ground_truth_fault="Standard ACL 10 was placed at the source ingress interface Gi0/0, blocking Host A from all destinations instead of placing an Extended ACL close to the destination.",
        ground_truth_fix="""R1# configure terminal
R1(config)# interface GigabitEthernet0/0
R1(config-if)# no ip access-group 10 in
R1(config)# ip access-list extended 110
R1(config-ext-nacl)# deny ip host 192.168.1.50 host 10.0.0.100
R1(config-ext-nacl)# permit ip any any
R1(config)# interface GigabitEthernet0/1
R1(config-if)# ip access-group 110 out
R1(config-if)# end"""
    ),
    NetworkCase(
        case_id="CASE-20",
        domain="ACL",
        concept_tag="ACL Blocking ICMP Diagnostic & PMTU",
        osi_layer="Layer 3",
        severity="Low",
        symptom="Large packets drop silently and network engineers cannot perform diagnostic ping/traceroute across WAN link.",
        topology_notes="WAN Edge Router R-WAN1 connecting to Branch.",
        show_outputs="""R-WAN1# show access-lists 150
Extended IP access list 150
    10 permit tcp any any established
    20 permit udp any any eq domain
    30 deny icmp any any (1450 matches)
    40 permit ip any any""",
        ground_truth_fault="Rule 30 explicitly denies all ICMP traffic, preventing echo-reply and ICMP Type 3 Code 4 (Fragmentation Needed) packets.",
        ground_truth_fix="""R-WAN1# configure terminal
R-WAN1(config)# ip access-list extended 150
R-WAN1(config-ext-nacl)# no 30
R-WAN1(config-ext-nacl)# 30 permit icmp any any unreachable
R-WAN1(config-ext-nacl)# 35 permit icmp any any echo-reply
R-WAN1(config-ext-nacl)# 36 permit icmp any any time-exceeded
R-WAN1(config-ext-nacl)# end"""
    ),

    # ---------------------------------------------------------
    # PHASE 2E: NAT & PAT (Cases 21 - 25)
    # ---------------------------------------------------------
    NetworkCase(
        case_id="CASE-21",
        domain="NAT",
        concept_tag="Missing IP NAT Inside Directive",
        osi_layer="Layer 3",
        severity="Critical",
        symptom="Internal clients on LAN cannot access internet hosts; `show ip nat translations` is completely empty.",
        topology_notes="Router R-Edge. Gi0/0 is LAN (192.168.1.1/24), Gi0/1 is WAN (203.0.113.2/30).",
        show_outputs="""R-Edge# show ip nat translations
(No translations active)

R-Edge# show running-config interface GigabitEthernet0/0
interface GigabitEthernet0/0
 ip address 192.168.1.1 255.255.255.0
 duplex auto
 speed auto
! (Missing ip nat inside)

R-Edge# show running-config interface GigabitEthernet0/1
interface GigabitEthernet0/1
 ip address 203.0.113.2 255.255.255.252
 ip nat outside""",
        ground_truth_fault="Interface GigabitEthernet0/0 (LAN) is missing the 'ip nat inside' configuration directive.",
        ground_truth_fix="""R-Edge# configure terminal
R-Edge(config)# interface GigabitEthernet0/0
R-Edge(config-if)# ip nat inside
R-Edge(config-if)# end"""
    ),
    NetworkCase(
        case_id="CASE-22",
        domain="NAT",
        concept_tag="Missing IP NAT Outside Directive",
        osi_layer="Layer 3",
        severity="Critical",
        symptom="LAN clients have 'ip nat inside' on internal interface, but packets are routed out to ISP with un-translated private IPs.",
        topology_notes="Router R-Edge. Gi0/0 is LAN, Serial0/0/0 is WAN to ISP.",
        show_outputs="""R-Edge# show running-config interface GigabitEthernet0/0
interface GigabitEthernet0/0
 ip address 10.0.0.1 255.255.255.0
 ip nat inside

R-Edge# show running-config interface Serial0/0/0
interface Serial0/0/0
 ip address 198.51.100.2 255.255.255.252
! (Missing ip nat outside)""",
        ground_truth_fault="Interface Serial0/0/0 (WAN) is missing the 'ip nat outside' configuration statement.",
        ground_truth_fix="""R-Edge# configure terminal
R-Edge(config)# interface Serial0/0/0
R-Edge(config-if)# ip nat outside
R-Edge(config-if)# end"""
    ),
    NetworkCase(
        case_id="CASE-23",
        domain="NAT",
        concept_tag="Missing PAT Overload Keyword",
        osi_layer="Layer 3",
        severity="High",
        symptom="Only the first single host that accesses the internet works; all subsequent client connections fail completely.",
        topology_notes="Router R-Gateway performing Dynamic NAT over public interface GigabitEthernet0/0/1.",
        show_outputs="""R-Gateway# show running-config | include ip nat inside source
ip nat inside source list 1 interface GigabitEthernet0/0/1

R-Gateway# show ip nat translations
Pro Inside global      Inside local       Outside local      Outside global
--- 203.0.113.1        192.168.1.5        ---                ---""",
        ground_truth_fault="The NAT statement is configured as 1-to-1 dynamic NAT without the 'overload' keyword, exhausting the single public IP after one host.",
        ground_truth_fix="""R-Gateway# configure terminal
R-Gateway(config)# no ip nat inside source list 1 interface GigabitEthernet0/0/1
R-Gateway(config)# ip nat inside source list 1 interface GigabitEthernet0/0/1 overload
R-Gateway(config)# end"""
    ),
    NetworkCase(
        case_id="CASE-24",
        domain="NAT",
        concept_tag="NAT Source ACL Subnet Exclusion",
        osi_layer="Layer 3",
        severity="High",
        symptom="Users in newly added VLAN 30 (192.168.30.0/24) cannot reach the internet, while VLAN 10 and 20 browse normally.",
        topology_notes="Router R1 has NAT enabled with ACL 1 matching traffic for translation.",
        show_outputs="""R1# show access-lists 1
Standard IP access list 1
    10 permit 192.168.10.0 0.0.0.255 (1520 matches)
    20 permit 192.168.20.0 0.0.0.255 (840 matches)
    (No permit statement for 192.168.30.0/24)

R1# show running-config | include ip nat inside source
ip nat inside source list 1 interface GigabitEthernet0/1 overload""",
        ground_truth_fault="Standard ACL 1 referenced by NAT does not permit subnet 192.168.30.0/24, preventing NAT translation for VLAN 30.",
        ground_truth_fix="""R1# configure terminal
R1(config)# access-list 1 permit 192.168.30.0 0.0.0.255
R1(config)# end"""
    ),
    NetworkCase(
        case_id="CASE-25",
        domain="NAT",
        concept_tag="Static NAT Port Translation Conflict",
        osi_layer="Layer 4",
        severity="High",
        symptom="External internet clients attempting to reach internal Web Server at public IP 203.0.113.10 port 80 are redirected to SSH port 22.",
        topology_notes="Router R1 configured with static NAT port forwarding for DMZ Web Server (192.168.5.10).",
        show_outputs="""R1# show running-config | include ip nat inside source static
ip nat inside source static tcp 192.168.5.10 22 203.0.113.10 80 extendable

R1# show ip nat translations
Pro Inside global      Inside local       Outside local      Outside global
tcp 203.0.113.10:80    192.168.5.10:22    ---                ---""",
        ground_truth_fault="Static NAT statement maps external port 80 to internal port 22 (SSH) instead of port 80 (HTTP).",
        ground_truth_fix="""R1# configure terminal
R1(config)# no ip nat inside source static tcp 192.168.5.10 22 203.0.113.10 80
R1(config)# ip nat inside source static tcp 192.168.5.10 80 203.0.113.10 80 extendable
R1(config)# end"""
    ),

    # ---------------------------------------------------------
    # PHASE 2F: WIRELESS, DNS & SERVICES (Cases 26 - 30)
    # ---------------------------------------------------------
    NetworkCase(
        case_id="CASE-26",
        domain="Wireless",
        concept_tag="Wireless Access Point SSID VLAN Mismatch",
        osi_layer="Layer 2",
        severity="High",
        symptom="Wireless laptop associates to 'Corporate-WiFi' SSID but cannot obtain an IP address or reach corporate intranet.",
        topology_notes="Lightweight AP AP-West connected to switch port Fa0/12. Corporate SSID expected on VLAN 50. Port Fa0/12 is untagged VLAN 1.",
        show_outputs="""SW-Access# show interfaces FastEthernet0/12 switchport
Name: Fa0/12
Switchport: Enabled
Administrative Mode: static access
Operational Mode: static access
Access Mode VLAN: 1 (default)

AP-West# show interfaces dot11Radio 0
SSID Corporate-WiFi : VLAN 50 (tagged)
Status: Carrier detect, beacon active""",
        ground_truth_fault="Switch port Fa0/12 connected to the AP is configured as access mode on VLAN 1 instead of a trunk port allowing VLAN 50.",
        ground_truth_fix="""SW-Access# configure terminal
SW-Access(config)# interface FastEthernet0/12
SW-Access(config-if)# switchport mode trunk
SW-Access(config-if)# switchport trunk allowed vlan 1,50,99
SW-Access(config-if)# end"""
    ),
    NetworkCase(
        case_id="CASE-27",
        domain="Wireless",
        concept_tag="WPA2 Pre-Shared Key Mismatch",
        osi_layer="Layer 2",
        severity="Medium",
        symptom="Mobile devices cannot associate with Wireless Router 'Branch-WAP'; client logs indicate 4-Way Handshake Failure.",
        topology_notes="Linksys/Cisco WRT300N Wireless Router configured with WPA2-Personal (AES).",
        show_outputs="""Branch-WAP# show wireless security
SSID: Staff-Secure
Security Mode: WPA2-Personal
Encryption: AES
Pre-Shared Key: CiscoSecure2026!

Client-Log> Association Request: Sent
Client-Log> Association Response: Success
Client-Log> 802.1X/WPA 4-Way Handshake: Failed (MIC mismatch / Key incorrect)
Client-Log> Deauthenticated from AP (Reason 15: 4-Way Handshake timeout)""",
        ground_truth_fault="Client configuration has an incorrect Pre-Shared Key ('CiscoSecure2025') mismatching the AP key ('CiscoSecure2026!').",
        ground_truth_fix="""Update client wireless profile with correct Pre-Shared Key: 'CiscoSecure2026!'."""
    ),
    NetworkCase(
        case_id="CASE-28",
        domain="DNS",
        concept_tag="Invalid Client DNS Server Assignment",
        osi_layer="Layer 7",
        severity="High",
        symptom="Users can ping external IP 8.8.8.8 successfully but cannot browse 'www.cisco.com' or any domain name.",
        topology_notes="Host PC-Finance. Primary DNS Server in lab is 192.168.1.10.",
        show_outputs="""PC-Finance> nslookup www.cisco.com
*** Can't find server address for '127.0.0.1': No response from server

PC-Finance> ipconfig
FastEthernet0 Connection:
   IP Address......................: 192.168.1.105
   Subnet Mask.....................: 255.255.255.0
   Default Gateway.................: 192.168.1.1
   DNS Servers.....................: 127.0.0.1""",
        ground_truth_fault="Client DNS server address is configured as loopback IP 127.0.0.1 instead of the active enterprise DNS server 192.168.1.10.",
        ground_truth_fix="""PC-Finance> ipconfig /setdns 192.168.1.10
(Or in Packet Tracer GUI: Desktop -> IP Configuration -> DNS Server: 192.168.1.10)"""
    ),
    NetworkCase(
        case_id="CASE-29",
        domain="DNS",
        concept_tag="DNS Service Stopped on Server",
        osi_layer="Layer 7",
        severity="Critical",
        symptom="All enterprise workstations report 'DNS Server not responding' when resolving local domain records.",
        topology_notes="Central Services Server Server-01 (192.168.10.200) hosting DNS service.",
        show_outputs="""Client> nslookup intranet.company.local 192.168.10.200
Server:  Server-01
Address:  192.168.10.200
*** Request to Server-01 timed out.
    timeout was 2 seconds.

Server-01# show services
Service           Status
-------           ------
HTTP              ON
DHCP              OFF
DNS               OFF
FTP               ON
EMAIL             OFF""",
        ground_truth_fault="The DNS Server daemon on Server-01 is turned OFF in Packet Tracer service configuration.",
        ground_truth_fix="""On Server-01 in Cisco Packet Tracer:
1. Open Server-01 -> Services Tab -> DNS.
2. Toggle DNS Service Radio Button from 'OFF' to 'ON'.
3. Verify record 'intranet.company.local' points to 192.168.10.50."""
    ),
    NetworkCase(
        case_id="CASE-30",
        domain="Wireless",
        concept_tag="Guest Wireless Isolation Failure",
        osi_layer="Layer 3",
        severity="Critical",
        symptom="Security audit alert: Unauthenticated guest Wi-Fi users in VLAN 90 can ping and access internal financial servers in 10.10.0.0/16.",
        topology_notes="Guest Wi-Fi Subnet: 192.168.90.0/24 (VLAN 90). Internal Corporate Subnet: 10.10.0.0/16 (VLAN 10). Router R-Core.",
        show_outputs="""Guest-Laptop> ping 10.10.1.100
Pinging 10.10.1.100 with 32 bytes of data:
Reply from 10.10.1.100: bytes=32 time=2ms TTL=127
Reply from 10.10.1.100: bytes=32 time=1ms TTL=127

R-Core# show running-config interface GigabitEthernet0/0.90
interface GigabitEthernet0/0.90
 encapsulation dot1Q 90
 ip address 192.168.90.1 255.255.255.0
! (No access-group applied)""",
        ground_truth_fault="Missing guest isolation ACL on sub-interface Gi0/0.90, allowing unrestricted inter-VLAN routing between Guest Wi-Fi and Corporate internal servers.",
        ground_truth_fix="""R-Core# configure terminal
R-Core(config)# ip access-list extended GUEST_ISOLATION
R-Core(config-ext-nacl)# deny ip 192.168.90.0 0.0.0.255 10.10.0.0 0.0.255.255
R-Core(config-ext-nacl)# permit ip 192.168.90.0 0.0.0.255 any
R-Core(config)# interface GigabitEthernet0/0.90
R-Core(config-subif)# ip access-group GUEST_ISOLATION in
R-Core(config-subif)# end"""
    )
]


def generate_dataset():
    """Validates all cases with Pydantic and exports to CSV and JSON."""
    print(f"Generating NetSage AI dataset with {len(CASES)} cases...")

    # Convert to dictionary records
    records = [case.model_dump() for case in CASES]

    # Save to CSV
    df = pd.DataFrame(records)
    csv_path = "data/cases.csv"
    df.to_csv(csv_path, index=False, encoding="utf-8")
    print(f"[OK] Exported CSV: {csv_path} ({len(df)} rows)")

    # Save to JSON
    json_path = "data/cases.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)
    print(f"[OK] Exported JSON: {json_path}")

    # Print summary statistics
    print("\n--- Dataset Distribution Summary ---")
    print(df["domain"].value_counts().to_string())
    print("\n--- OSI Layer Breakdown ---")
    print(df["osi_layer"].value_counts().to_string())
    print("\n--- Severity Breakdown ---")
    print(df["severity"].value_counts().to_string())


if __name__ == "__main__":
    generate_dataset()

