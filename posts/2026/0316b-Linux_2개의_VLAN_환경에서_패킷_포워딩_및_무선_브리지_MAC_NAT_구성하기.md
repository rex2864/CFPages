## Linux 2개의 VLAN 환경에서 패킷 포워딩 및 무선 브리지 MAC NAT 구성하기

(gemini로 작성됨)

단일 리눅스 서버나 라우터에서 여러 개의 VLAN을 나누고, 각 네트워크 대역 간의 패킷을 정교하게 포워딩해야 하는 경우가 있습니다. 특히 무선 인터페이스(WLAN)를 브리지로 묶을 때는 MAC 주소 문제로 통신이 차단되기도 하는데, 이때 `iptables`와 `ebtables`를 조합하면 문제를 말끔히 해결할 수 있습니다.

이번 글에서는 2개의 VLAN(ID 4, 5)을 구성하고 NAT 및 정책 라우팅을 설정하는 방법, 그리고 무선 AP와의 통신을 위한 L2 계층의 MAC NAT 설정까지 단계별로 알아보겠습니다.

### 1. IP 포워딩 활성화 및 VLAN 인터페이스 생성

리눅스 장비가 라우터 역할을 수행하려면 가장 먼저 패킷 포워딩 기능이 켜져 있어야 합니다.

```bash
#!/bin/sh

# 1. IP 포워딩 활성화
sysctl -w net.ipv4.ip_forward=1
```

> **쉘 스크립트 작성 팁:**
> 스크립트 첫 줄의 `#!/bin/sh`를 다양한 리눅스 환경(Alpine, Ubuntu 등)에서의 이식성을 위해 `#!/usr/bin/env bash`나 `#!/usr/bin/env sh`로 변경하여 안내하는 것도 좋은 방법입니다.

이어서 외부 네트워크 인터페이스(`enp0s8`)와 내부 네트워크 인터페이스(`enp0s9`) 각각에 VLAN ID 4번과 5번을 태깅한 가상 인터페이스를 생성하고 IP를 할당합니다.

```bash
# 외부 인터페이스(enp0s8) 활성화 및 VLAN 4, 5 생성
ip link set enp0s8 up

ip link add link enp0s8 name evlan4 type vlan id 4
ip addr add 192.168.84.1/24 brd + dev evlan4
ip link set evlan4 up

ip link add link enp0s8 name evlan5 type vlan id 5
ip addr add 192.168.85.1/24 brd + dev evlan5
ip link set evlan5 up

# 내부 인터페이스(enp0s9) 활성화 및 VLAN 4, 5 생성
ip link set enp0s9 up

ip link add link enp0s9 name ivlan4 type vlan id 4
ip addr add 192.168.94.1/24 brd + dev ivlan4
ip link set ivlan4 up

ip link add link enp0s9 name ivlan5 type vlan id 5
ip addr add 192.168.95.1/24 brd + dev ivlan5
ip link set ivlan5 up
```

### 2. iptables를 이용한 1:1 NAT (DNAT / SNAT) 설정

외부에서 들어오는 트래픽을 내부의 특정 IP로 전달하고, 내부에서 나가는 트래픽을 외부 인터페이스의 IP로 변환하기 위해 `iptables`의 NAT 테이블을 설정합니다.

```bash
# VLAN 4 트래픽 NAT 설정 (192.168.94.x 대역)
iptables -t nat -A PREROUTING -i evlan4 -j DNAT --to-destination 192.168.94.2
iptables -t nat -A POSTROUTING -o ivlan4 -j SNAT --to-source 192.168.94.1

# VLAN 5 트래픽 NAT 설정 (192.168.95.x 대역)
iptables -t nat -A PREROUTING -i evlan5 -j DNAT --to-destination 192.168.95.2
iptables -t nat -A POSTROUTING -o ivlan5 -j SNAT --to-source 192.168.95.1
```

### 3. 정책 기반 라우팅(PBR) 및 MASQUERADE 설정

VLAN 4와 VLAN 5의 트래픽이 서로 섞이지 않고, 각자의 전용 라우팅 테이블을 타도록 정책을 추가합니다.

```bash
# VLAN 4를 위한 라우팅 테이블(table 4) 생성 및 외부 통신용 MASQUERADE
ip rule add priority 4 iif ivlan4 table 4
ip route add default dev evlan4 table 4
iptables -t nat -A POSTROUTING -o evlan4 -j MASQUERADE

# VLAN 5를 위한 라우팅 테이블(table 5) 생성 및 외부 통신용 MASQUERADE
ip rule add priority 5 iif ivlan5 table 5
ip route add default dev evlan5 table 5
iptables -t nat -A POSTROUTING -o evlan5 -j MASQUERADE

# Proxy ARP 활성화
sysctl -w net.ipv4.conf.all.proxy_arp=1
```

* `proxy_arp=1`: 라우터가 대신 ARP 요청에 응답할 수 있게 하여, 분리된 네트워크 간의 투명한 통신을 돕습니다.

### 4. ebtables를 활용한 무선 브리지 MAC NAT (L2 설정)

무선 AP에 연결된 Wi-Fi 인터페이스(`wlan0`)를 브리지(Bridge)에 포함시킬 때, 일반적으로 AP는 다중 MAC 주소(4-address mode 미지원 시)를 허용하지 않아 통신이 드롭되는 문제가 발생합니다.

이를 해결하기 위해 L2(데이터 링크 계층) 방화벽인 `ebtables`를 사용하여 **MAC 주소를 변조(NAT)**해야 합니다.

**1) 브리지에서 AP로 나가는 프레임 (Source MAC 변경)**

모든 프레임의 출발지 MAC 주소를 브리지 장비 자체의 MAC 주소로 속여서 내보냅니다.

```bash
ebtables -t nat -A POSTROUTING -o wlan0 -j snat --to-src $MAC_OF_BRIDGE --snat-arp --snat-target ACCEPT
```

**2) AP에서 브리지 뒤쪽 기기들로 들어오는 프레임 (Destination MAC 변경)**

AP에서 들어오는 트래픽이 브리지 뒤에 있는 실제 머신들에게 잘 도착하도록, 목적지 IP에 맞춰 MAC 주소를 다시 원래 기기의 MAC으로 되돌려 줍니다.

*(아래의 `$IP`와 `$MAC`을 실제 연결된 내부 머신의 정보로 치환해야 합니다.)*

```bash
ebtables -t nat -A PREROUTING -p IPv4 -i wlan0 --ip-dst $IP -j dnat --to-dst $MAC --dnat-target ACCEPT
ebtables -t nat -A PREROUTING -p ARP -i wlan0 --arp-ip-dst $IP -j dnat --to-dst $MAC --dnat-target ACCEPT
```

위의 L3(IP) 라우팅 설정과 L2(MAC) 브리지 설정을 환경에 맞게 적용하면, 복잡한 VLAN 및 무선 네트워크 환경에서도 안정적인 패킷 포워딩을 구현할 수 있습니다.

---

Date: 2026. 03. 16

Tags: Linux, 네트워크, VLAN, iptables, ebtables, NAT, PolicyRouting, 네트워크엔지니어, 서버관리
