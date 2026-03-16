## Raspberry Pi IPv6-Only 테스트를 위한 DNS64 NAT64 무선 공유기(AP) 만들기

(gemini로 작성됨)

모바일 앱 개발(특히 Apple App Store 심사)이나 차세대 네트워크 환경을 테스트하기 위해 순수 IPv6 환경이 필요할 때가 있습니다. 하지만 외부 인터넷망은 여전히 IPv4를 사용하는 경우가 많습니다.

이 글에서는 라즈베리파이를 **무선 AP(공유기)**로 만들고, **DNS64(Unbound)**와 **NAT64(Jool)** 기술을 적용하여 "내부망은 IPv6 전용, 외부망은 IPv4로 변환하여 통신"하는 완벽한 테스트 환경을 구축하는 방법을 단계별로 알아보겠습니다.

> **구성 환경 (Topology)**
> * **외부망(WAN, eth0)**: `192.168.1.10` (기존 공유기와 연결)
> * **내부망(LAN/AP, wlan0)**: `192.168.100.1` (IPv4) / `fc01:0:0:1::1` (IPv6)
> * **무선 SSID**: `kyle-rpi3`

### 1. 네트워크 인터페이스 고정 IP 설정

먼저 무선 랜카드(`wlan0`)와 유선 랜카드(`eth0`)에 고정 IP를 할당합니다.

**1) wlan0 설정 (무선 AP용 인터페이스)**

```bash
sudo vi /etc/network/interfaces.d/wlan0
```

```text
allow-hotplug wlan0
iface wlan0 inet static
    address 192.168.100.1
    netmask 255.255.255.0
iface wlan0 inet6 static
    address fc01:0:0:1::1
    netmask 64
```

**2) eth0 설정 (외부 인터넷 연결용)**

```bash
sudo vi /etc/dhcpcd.conf
```

```text
interface eth0
static ip_address=192.168.1.10/24
static routers=192.168.0.1
static domain_name_servers=192.168.0.1 8.8.8.8
```

설정을 마친 후 `sudo reboot` 명령어로 라즈베리파이를 재부팅합니다.

### 2. IP 포워딩(라우팅) 활성화

라즈베리파이가 인터페이스 간에 패킷을 전달(라우팅)할 수 있도록 커널 파라미터를 수정합니다.

```bash
sudo vi /etc/sysctl.conf
```

```text
net.ipv4.ip_forward=1
net.ipv6.conf.all.forwarding=1
net.ipv6.conf.wlan0.accept_ra=2
net.ipv4.conf.all.accept_source_route=1
```

변경 사항을 즉시 적용합니다.

```bash
sudo sysctl --system
```

### 3. 무선 AP (Access Point) 모드 설정

`hostapd`를 설치하여 라즈베리파이의 무선 랜카드를 공유기처럼 신호를 쏘도록 만듭니다.

```bash
sudo apt-get install hostapd
sudo vi /etc/default/hostapd
```

```text
# 설정 파일 경로를 지정해 줍니다.
DAEMON_CONF="/etc/hostapd/hostapd.conf"
```

실제 Wi-Fi 이름과 비밀번호를 설정합니다.

```bash
sudo vi /etc/hostapd/hostapd.conf
```

```text
interface=wlan0
driver=nl80211
ssid=kyle-rpi3
hw_mode=g
channel=7
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=1qaz2wsx  # 사용할 Wi-Fi 비밀번호
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
```

설정이 완료되면 데몬 마스크를 해제하고 서비스를 시작합니다.

```bash
sudo systemctl unmask hostapd
sudo systemctl start hostapd
```

### 4. DHCP 및 Router Advertisement 설정

`dnsmasq`를 사용하여 AP에 접속한 기기들에게 IP(IPv4/IPv6)와 DNS 주소를 자동으로 할당합니다.

```bash
sudo apt-get install dnsmasq
sudo vi /etc/dnsmasq.conf
```

```text
port=0
interface=wlan0
bind-interfaces
domain-needed
bogus-priv
server=192.168.100.1
server=fc01:0:0:1::1
local=/kyle-rpi3/
domain=kyle-rpi3
dhcp-fqdn
enable-ra
dhcp-range=192.168.100.10,192.168.100.100,255.255.255.0,12h
dhcp-range=::,constructor:wlan0,slaac
dhcp-option=option:router,192.168.100.1
dhcp-option=option:dns-server,192.168.100.1
dhcp-option=option6:dns-server,fc01:0:0:1::1
dhcp-authoritative
```

```bash
sudo systemctl restart dnsmasq
```

### 5. DNS64 설정 (Unbound)

IPv6-Only 단말기가 IPv4 전용 서버(예: `google.com`)에 접속하려 할 때, 가상의 IPv6 주소를 합성해서 알려주는 역할을 합니다.

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

### 6. NAT64 설정 (Jool)

DNS64가 알려준 가상의 IPv6 주소(`64:ff9b::/96`)로 패킷이 들어오면, 이를 실제 IPv4 주소로 변환하여 외부망(`eth0`)으로 내보내는 실질적인 번역기 역할입니다. 리눅스 커널 모듈인 **Jool**을 컴파일하여 사용합니다.

```bash
# 필수 빌드 도구 설치
sudo apt-get install raspberrypi-kernel-headers libnl-genl-3-dev libxtables-dev dkms git autoconf libtool iptables

# Jool 소스 다운로드 및 설치
wget https://github.com/NICMx/Jool/releases/download/v4.1.7/jool-4.1.7.tar.gz
tar -xzf jool-4.1.7.tar.gz
sudo dkms install jool-4.1.7/
cd jool-4.1.7/
./configure
make
sudo make install
sudo depmod -a

# 커널 모듈 로드 및 Jool 인스턴스 생성
sudo modprobe jool pool6=64:ff9b::/96
sudo jool instance add "example" --iptables --pool6 64:ff9b::/96

# iptables/ip6tables 트래픽 포워딩 룰 적용
sudo ip6tables -t mangle -A PREROUTING -d 64:ff9b::/96 -j JOOL --instance "example"
sudo iptables -t mangle -A PREROUTING -d 192.168.1.10 -p tcp --dport 61001:65535 -j JOOL --instance "example"
sudo iptables -t mangle -A PREROUTING -d 192.168.1.10 -p udp --dport 61001:65535 -j JOOL --instance "example"
sudo iptables -t mangle -A PREROUTING -d 192.168.1.10 -p icmp -j JOOL --instance "example"
```

### Bonus: 일반 계정으로 원격 패킷 실시간 캡처하기 (tcpdump + Wireshark)

구축한 환경에서 패킷이 제대로 변환되는지 확인하려면 패킷 분석이 필수입니다. 매번 `root` 권한을 사용할 필요 없이, 특정 일반 계정(예: `rex2864`)에게만 캡처 권한을 부여하고 로컬 PC의 Wireshark로 실시간 파이핑(Piping)하는 방법입니다.

```bash
# tcpdump 설치 및 pcap 그룹 생성
sudo apt-get install tcpdump
sudo groupadd pcap

# 캡처를 허용할 사용자(예: rex2864)를 pcap 그룹에 추가
sudo usermod -a -G pcap rex2864
sudo chgrp pcap /usr/bin/tcpdump
sudo chmod 750 /usr/bin/tcpdump

# root 권한 없이 네트워크 캡처를 할 수 있도록 커널 Capability 부여
sudo setcap cap_net_raw,cap_net_admin=eip /usr/bin/tcpdump
```

이제 로컬 Windows PC의 명령 프롬프트(CMD)에서 아래 명령어를 통해 라즈베리파이의 패킷을 실시간으로 분석할 수 있습니다!

```cmd
ssh rex2864@192.168.1.10 tcpdump -i any -U -s0 -w - 'not port 22' | "c:\Program Files\Wireshark\Wireshark.exe" -k -i -
```

---

Date: 2026. 03. 16

Tags: RaspberryPi, IPv6, DNS64, NAT64, Jool, 네트워크구축, 서버관리, 네트워크엔지니어
