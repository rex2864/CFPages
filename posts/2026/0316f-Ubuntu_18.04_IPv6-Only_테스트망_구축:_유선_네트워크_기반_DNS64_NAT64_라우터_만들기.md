## Ubuntu 18.04 IPv6-Only 테스트망 구축: 유선 네트워크 기반 DNS64 NAT64 라우터 만들기

(gemini로 작성됨)

지난번 라즈베리파이를 활용한 무선 AP 기반의 IPv6 테스트 환경 구축에 이어, 이번에는 **Ubuntu 18.04 서버(또는 VM) 환경에서 2개의 유선 랜카드(NIC)를 활용하여 완벽한 IPv6-Only 라우터를 만드는 방법**을 정리해 보았습니다.

우분투 환경에 맞춰 네트워크 설정 도구인 `netplan`을 사용하며, 무선 설정이 제외되어 한결 간결해진 구성입니다. 내부망 기기들은 오직 IPv6만 사용하지만, 우분투 서버가 DNS64(Unbound)와 NAT64(Jool)를 거쳐 외부망(IPv4)과 통신할 수 있도록 다리를 놓아줍니다.

> **💡 구성 환경 (Topology)**
> * **외부망(WAN, enp0s3)**: `192.168.1.10` (IPv4 전용, 기존 공유기와 연결)
> * **내부망(LAN, enp0s8)**: `fc01:0:0:1::1/64` (IPv6 전용, 하위 테스트 기기들과 연결)
> * **OS**: Ubuntu 18.04 LTS

### 1. 네트워크 인터페이스 고정 IP 설정 (Netplan)

Ubuntu 18.04부터 기본으로 채택된 `netplan`을 사용하여 외부망(IPv4)과 내부망(IPv6) 인터페이스의 IP를 고정으로 할당합니다.

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

설정 저장 후, 시스템을 재부팅(`sudo reboot`) 하거나 `sudo netplan apply`를 실행하여 네트워크 설정을 적용합니다.

### 2. IP 포워딩(라우팅) 활성화

우분투 서버가 `enp0s3`와 `enp0s8` 인터페이스 사이에서 트래픽을 넘겨줄 수 있도록 커널의 포워딩 기능을 켭니다.

```bash
sudo vi /etc/sysctl.conf
```

```text
net.ipv4.ip_forward=1
net.ipv6.conf.all.forwarding=1
net.ipv6.conf.enp0s8.accept_ra=2
net.ipv4.conf.all.accept_source_route=1
```

변경 사항을 즉시 적용합니다.

```bash
sudo sysctl --system
```

### 3. 내부망 DHCPv6 및 RA 설정 (dnsmasq)

내부망(`enp0s8`)에 연결된 클라이언트 단말기들이 IPv6 주소와 DNS 정보를 자동으로 받아 갈 수 있도록 `dnsmasq`를 구성합니다. SLAAC(Stateless Address Autoconfiguration) 방식을 사용합니다.

```bash
sudo apt-get install dnsmasq
sudo vi /etc/dnsmasq.conf
```

```text
port=0
interface=enp0s8
bind-interfaces
domain-needed
bogus-priv
server=fc01:0:0:1::1
local=/ipv6_router/
domain=ipv6_router
dhcp-fqdn
enable-ra
dhcp-range=::,constructor:enp0s3,slaac
dhcp-option=option6:dns-server,fc01:0:0:1::1
dhcp-authoritative
```

```bash
sudo systemctl restart dnsmasq
```

### 4. DNS64 설정 (Unbound)

단말기가 IPv4 전용 서버에 접속하려고 할 때, 이를 속여서 가상의 IPv6 주소(`64:ff9b::/96`)로 맵핑해 주는 DNS64 서비스를 구축합니다.

```bash
sudo apt-get install unbound
sudo vi /etc/unbound/unbound.conf.d/dns64.conf
```

```text
server:
  verbosity: 2
  pidfile: "/var/run/unbound.pid"
  use-syslog: yes
  module-config: "dns64 iterator"
  dns64-prefix: 64:ff9b::/96
  dns64-synthall: yes
  interface: ::0
  port: 53
  access-control: ::0/0 allow

forward-zone:
  name: "."
  forward-addr: 8.8.8.8
```

```bash
sudo systemctl restart unbound
```

### 5. NAT64 설정 (Jool)

DNS64가 발급해 준 가상 IPv6 대역(`64:ff9b::/96`)으로 들어온 트래픽의 껍데기를 실제 IPv4 패킷으로 변환하여 외부로 내보냅니다. 리눅스 커널 모듈인 **Jool**을 사용합니다.

우분투 환경에 맞게 `pkg-config`와 `build-essential` 등 필수 빌드 패키지들을 먼저 설치합니다.

```bash
# 빌드 필수 패키지 설치
sudo apt-get install build-essential linux-libc-dev libnl-genl-3-dev libxtables-dev dkms git autoconf libtool iptables pkg-config

# Jool 소스코드 다운로드 및 설치
wget https://github.com/NICMx/Jool/releases/download/v4.1.7/jool-4.1.7.tar.gz
tar -xzf jool-4.1.7.tar.gz
sudo dkms install jool-4.1.7/
cd jool-4.1.7/
./configure
make
sudo make install
sudo depmod -a

# 커널 모듈 로드 및 Jool 인스턴스 활성화
sudo modprobe jool pool6=64:ff9b::/96
sudo jool instance add "example" --iptables --pool6 64:ff9b::/96

# 포워딩을 위한 iptables/ip6tables 룰 적용
sudo ip6tables -t mangle -A PREROUTING -d 64:ff9b::/96 -j JOOL --instance "example"
sudo iptables -t mangle -A PREROUTING -d 192.168.1.10 -p tcp --dport 61001:65535 -j JOOL --instance "example"
sudo iptables -t mangle -A PREROUTING -d 192.168.1.10 -p udp --dport 61001:65535 -j JOOL --instance "example"
sudo iptables -t mangle -A PREROUTING -d 192.168.1.10 -p icmp -j JOOL --instance "example"
```

### 6. 일반 계정으로 원격 실시간 패킷 캡처 설정 (Bonus)

네트워크가 의도한 대로 잘 번역(NAT)되고 있는지 확인하려면 트래픽 캡처가 필수입니다. `root` 계정을 직접 사용하지 않고, 일반 계정에게 `tcpdump` 실행 권한을 부여하여 로컬 PC의 Wireshark로 실시간 분석하는 방법입니다.

```bash
# tcpdump 설치 및 pcap 그룹 생성
sudo apt-get install tcpdump
sudo groupadd pcap

# 캡처를 허용할 계정(예: rex2864) 등록 및 권한 설정
sudo usermod -a -G pcap rex2864
sudo chgrp pcap /usr/sbin/tcpdump
sudo chmod 750 /usr/sbin/tcpdump

# 커널 캡처 권한(Capability) 부여
sudo setcap cap_net_raw,cap_net_admin=eip /usr/sbin/tcpdump
```

설정을 마친 후, Windows PC의 터미널(CMD/PowerShell)에서 파이프(`|`)를 이용해 아래와 같이 접속하면 실시간으로 패킷을 엿볼 수 있습니다.

```cmd
# 일반 계정(rex2864)으로 접속 시
ssh rex2864@192.168.1.10 tcpdump -i any -U -s0 -w - 'not port 22' | "c:\Program Files\Wireshark\Wireshark.exe" -k -i -

# (참고) root 계정 사용 시
ssh root@192.168.1.4 tcpdump -i any -U -s0 -w - 'not port 22' | "c:\Program Files\Wireshark\Wireshark.exe" -k -i -
```

---

Date: 2026. 03. 16

Tags: Ubuntu1804, IPv6, DNS64, NAT64, Jool, Netplan, 네트워크라우팅, 테스트환경구축, Wireshark
