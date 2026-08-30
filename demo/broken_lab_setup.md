# NetSage AI: Demonstration Packet Tracer Lab Setup Guide

## 🌐 Topology Overview: Campus Multi-VLAN Inter-VLAN Routing with ACL Security

This scenario models a standard university or enterprise branch campus network where Student workstations in **VLAN 10** (`192.168.10.0/24`) attempt to access the **Campus Web Server** in **VLAN 20** (`192.168.20.80`) via a Router-on-a-Stick gateway (`R1`), but access fails due to an implicit ACL drop and sub-interface encapsulation mismatch.

```text
               +-------------------------------------------------+
               |             Router R1 (Cisco 2911)              |
               |  Gi0/0.10: 192.168.10.1/24 (VLAN 10 Dot1Q)      |
               |  Gi0/0.20: 192.168.20.1/24 (VLAN 20 Dot1Q)      |
               +-----------------------+-------------------------+
                                       | 802.1Q Trunk (Gi0/1)
               +-----------------------+-------------------------+
               |           Switch SW-Core1 (Cisco 2960)          |
               +-----------+-------------------------+-----------+
                           | Fa0/5 (VLAN 10)         | Fa0/10 (VLAN 20)
                           |                         |
               +-----------+-----------+ +-----------+-----------+
               |  Student PC (PC-01)   | |  Campus Web Server    |
               |  IP: 192.168.10.25    | |  IP: 192.168.20.80    |
               |  GW: 192.168.10.1     | |  GW: 192.168.20.1     |
               +-----------------------+ +-----------------------+
```

---

## 🛑 The Broken Configuration State

### 1. Router R1 Broken Configuration (`R1-broken.cfg`)
```cisco
hostname R1
!
interface GigabitEthernet0/0
 no ip address
 duplex auto
 speed auto
 no shutdown
!
interface GigabitEthernet0/0.10
 encapsulation dot1Q 10
 ip address 192.168.10.1 255.255.255.0
!
interface GigabitEthernet0/0.20
 encapsulation dot1Q 20
 ip address 192.168.20.1 255.255.255.0
 ip access-group 101 out
!
! FAULT: ACL 101 permits only ICMP, implicitly dropping TCP Port 80 (HTTP) traffic
ip access-list extended 101
 permit icmp 192.168.10.0 0.0.0.255 192.168.20.0 0.0.0.255
!
end
```

### 2. Switch SW-Core1 Broken Configuration (`SW-Core1-broken.cfg`)
```cisco
hostname SW-Core1
!
vlan 10
 name Students
!
vlan 20
 name Servers
!
interface FastEthernet0/5
 switchport access vlan 10
 switchport mode access
!
interface FastEthernet0/10
 switchport access vlan 20
 switchport mode access
!
! Uplink to Router R1
interface GigabitEthernet0/1
 switchport mode trunk
 switchport trunk allowed vlan 10,20
!
end
```

---

## 🛠️ The Solved / Remediated Configuration State

### Router R1 Fixed Configuration (`R1-fixed.cfg`)
```cisco
configure terminal
ip access-list extended 101
 20 permit tcp 192.168.10.0 0.0.0.255 host 192.168.20.80 eq 80
 30 permit tcp 192.168.10.0 0.0.0.255 host 192.168.20.80 eq 443
end
copy running-config startup-config
```

---

## 🧪 Verification Commands

1. **On Student PC (PC-01):**
   ```text
   PC> ping 192.168.20.80
   Reply from 192.168.20.80: bytes=32 time<1ms TTL=127 (ICMP succeeds)

   PC> curl http://192.168.20.80
   <!DOCTYPE html><html><h1>Welcome to Campus Portal</h1></html> (HTTP succeeds)
   ```

2. **On Router R1:**
   ```text
   R1# show access-lists 101
   Extended IP access list 101
       10 permit icmp 192.168.10.0 0.0.0.255 192.168.20.0 0.0.0.255 (12 matches)
       20 permit tcp 192.168.10.0 0.0.0.255 host 192.168.20.80 eq 80 (45 matches)
       30 permit tcp 192.168.10.0 0.0.0.255 host 192.168.20.80 eq 443
   ```
