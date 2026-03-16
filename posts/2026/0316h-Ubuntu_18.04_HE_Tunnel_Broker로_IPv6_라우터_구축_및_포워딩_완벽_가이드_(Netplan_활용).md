## Ubuntu 18.04 HE Tunnel Broker로 IPv6 라우터 구축 및 포워딩 완벽 가이드 (Netplan 활용)

(gemini로 작성됨)

통신사에서 IPv6를 지원하지 않는 환경에서 IPv6-Only 네트워크망을 테스트해야 할 때, **HE Tunnel Broker(Hurricane Electric)** 서비스는 아주 훌륭한 대안입니다.

이전 포스팅에서는 라즈베리파이를 활용한 무선 AP 기반의 구축 방법을 알아보았는데요. 이번 글에서는 **Ubuntu 18.04 서버(또는 VM)에서 2개의 유선 랜카드를 사용하여 완벽한 IPv6 라우터 및 포워딩 환경을 구축하는 방법**을 정리해 보겠습니다. 우분투의 기본 네트워크 도구인 `netplan`을 사용하여 터널을 매우 깔끔하게 구성할 수 있습니다.

> **⚠️ 필수 사전 준비 (공유기 설정)**
> 우분투 서버가 상단 공유기(Router) 아래에 연결된 경우, HE 터널의 프로토콜 41(IPv6 in IPv4) 패킷이 정상적으로 들어올 수 있도록 **공유기 설정에서 우분투 서버의 IP(`192.168.1.10`)를 DMZ로 설정**해야 합니다.
> * 또한 공유기에 할당된 **공인 외부 IPv4 주소(예: 125.176.11.144)**를 미리 확인하여 HE Tunnel Broker 웹사이트의 Endpoint로 등록해 두어야 합니다.

### 1. 네트워크 인터페이스 기본 설정 (Netplan)

외부 인터넷과 연결될 인터페이스(`enp0s3`)는 IPv4 고정 IP로, 내부 테스트 기기들이 연결될 인터페이스(`enp0s8`)는 IPv6 대역으로 분리하여 설정합니다.

```bash
sudo vi /etc/netplan/00-installer-config.yaml
```

```yaml
network:
  ethernets:
    enp0s3:
      addresses:
      - 192.168.1.10/24
      gateway4: 192.168.0.1
      nameservers:
        addresses:
        - 8.8.8.8
    enp0s8:
      addresses:
      - fc01:0:0:1::1/64
      nameservers: {}
  version: 2
```

설정을 저장한 후 적용합니다.

```bash
sudo netplan apply
```

### 2. HE IPv6 터널 인터페이스 추가 (Netplan sit 모드)

HE Tunnel Broker에서 발급받은 정보를 바탕으로 `netplan` 설정 파일에 터널(Tunnel) 인터페이스를 바로 추가합니다. 이전 방식들보다 훨씬 직관적입니다.

```bash
sudo vi /etc/netplan/00-installer-config.yaml
```

아래의 `tunnels` 구문을 파일 하단에 추가합니다.

```yaml
network:
  version: 2
  tunnels:
    he-ipv6:
      mode: sit
      remote: 216.218.221.42          # HE Tunnel Server IPv4 주소
      local: 192.168.1.10             # 우분투 서버의 로컬 IPv4 주소
      addresses:
        - 2001:470:35:79b::2/64       # 발급받은 Client IPv6 주소
      gateway6: 2001:470:35:79b::1    # HE Tunnel Server IPv6 주소
```

마찬가지로 설정을 시스템에 적용합니다.

```bash
sudo netplan apply
```

### 3. DHCPv6 및 RA 설정 (dnsmasq)

내부망(`enp0s8`)에 연결된 단말기들에게 SLAAC 방식으로 IPv6 주소를 분배하고, Google의 DNS64 주소를 할당하도록 `dnsmasq`를 세팅합니다.

```bash
sudo apt-get install dnsmasq
sudo vi /etc/dnsmasq.conf
```

```text
interface=enp0s8
bind-interfaces
domain-needed
bogus-priv

# DNS Server (Google DNS64)
server=2001:4860:4860::6464

# Local DNS name
local=/<ubuntu_hostname>/
domain=<ubuntu_hostname>
dhcp-fqdn

# DHCP 및 RA(Router Advertisement) 설정
enable-ra
dhcp-range=::,constructor:enp0s8,slaac
dhcp-option=option6:dns-server,2001:4860:4860::6464
dhcp-authoritative
```

* `<ubuntu_hostname>` 부분은 실제 사용 중인 우분투의 호스트명으로 변경해 주세요.

```bash
sudo systemctl restart dnsmasq
```

### 4. IPv6 포워딩 활성화 및 NAT6 라우팅 설정

서버가 라우터로서 패킷을 넘겨줄 수 있도록 커널 포워딩을 켜고, `ip6tables`를 이용해 내부망 트래픽이 터널(`he-ipv6`)을 타고 나갈 수 있도록 MASQUERADE 처리를 해줍니다.

**1) 커널 포워딩 활성화**

```bash
sudo vi /etc/sysctl.conf
```

```text
# 아래 두 줄의 주석(#)을 해제하거나 추가합니다.
net.ipv4.ip_forward=1
net.ipv6.conf.all.forwarding=1
```

```bash
sudo sysctl -p
```

**2) ip6tables 트래픽 포워딩 규칙 적용**

DNS 요청(UDP 53)을 Google DNS64로 강제 우회시키고, 터널을 통해 외부로 나가는 패킷의 출발지 주소를 변환(SNAT/MASQUERADE)합니다.

```bash
sudo ip6tables -t nat -A PREROUTING -i enp0s8 -p udp --dport 53 -j DNAT --to-destination 2001:4860:4860::6464
sudo ip6tables -t nat -A POSTROUTING -o he-ipv6 -p udp --dport 53 -j SNAT --to-source 2001:470:35:79b::2
sudo ip6tables -t nat -A POSTROUTING -o he-ipv6 -j MASQUERADE
```

### 5. 트래픽 실시간 모니터링 (Bonus)

구성된 라우터 환경에서 패킷이 제대로 터널을 타고 나가는지 로컬 PC의 Wireshark로 실시간 분석이 가능합니다. (미리 서버에 `tcpdump` 관련 사용자 권한이 세팅되어 있어야 합니다.)

Windows PC의 명령 프롬프트(CMD)에서 아래와 같이 실행합니다.

```cmd
ssh rex2864@192.168.1.10 tcpdump -i any -U -s0 -w - 'not port 22' | "c:\Program Files\Wireshark\Wireshark.exe" -k -i -
```

---

Date: 2026. 03. 16

Tags: Ubuntu1804, IPv6, TunnelBroker, Netplan, dnsmasq, iptables, 네트워크라우팅, 서버관리, 네트워크테스트
