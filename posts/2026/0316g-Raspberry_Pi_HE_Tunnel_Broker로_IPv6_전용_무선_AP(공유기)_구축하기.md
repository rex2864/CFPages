## Raspberry Pi HE Tunnel Broker로 IPv6 전용 무선 AP(공유기) 구축하기

(gemini로 작성됨)

통신사에서 IPv6를 지원하지 않는 환경에서 모바일 앱 심사(IPv6-Only 통신 필수)나 네트워크 테스트를 진행해야 할 때가 있습니다. 이럴 때는 무료 서비스인 **HE Tunnel Broker(Hurricane Electric)**를 이용해 기존 IPv4 망 위에 IPv6 터널을 뚫는 방식을 사용할 수 있습니다.

이번 글에서는 라즈베리파이에 HE IPv6 터널을 연결하고, `hostapd`와 `dnsmasq`를 활용해 접속하는 기기들에게 순수 IPv6 환경을 제공하는 무선 AP(공유기) 구축 방법을 단계별로 알아봅니다.

> **💡 사전 준비 사항**
> * [tunnelbroker.net](https://tunnelbroker.net/) 에 가입하여 'Regular Tunnel'을 생성해야 합니다.
> * 발급받은 터널의 Endpoint IPv4 주소와 할당된 IPv6 대역(`2001:470...`) 정보를 준비해 주세요.

### 1. 유무선 네트워크 인터페이스 설정

먼저 외부 인터넷과 연결될 유선 랜(`eth0`)은 IPv4로, 내부 기기들이 접속할 무선 랜(`wlan0`)은 IPv6 전용으로 IP를 고정합니다.

**1) eth0 설정 (외부망)**

```bash
sudo vi /etc/dhcpcd.conf
```

```text
interface eth0
static ip_address=192.168.1.10/24
static routers=192.168.0.1
static domain_name_servers=192.168.0.1 8.8.8.8
```

**2) wlan0 설정 (내부망 AP용)**

```bash
sudo vi /etc/network/interfaces.d/wlan0
```

```text
allow-hotplug wlan0
iface wlan0 inet6 static
    address fc01:0:0:1::1
    netmask 64
```

적용을 위해 라즈베리파이를 재부팅(`sudo reboot`)합니다.

### 2. HE IPv6 터널 인터페이스 생성

HE Tunnel Broker에서 발급받은 정보를 바탕으로 `he-ipv6`라는 터널 인터페이스를 생성합니다.

```bash
sudo vi /etc/network/interfaces.d/he-ipv6
```

```text
auto he-ipv6
iface he-ipv6 inet6 v4tunnel
    address 2001:470:35:79b::2       # 발급받은 Client IPv6 주소
    netmask 64
    endpoint 216.218.221.42          # HE Tunnel Server IPv4 주소
    local 192.168.1.10               # 라즈베리파이의 로컬 IPv4 주소
    ttl 255
    gateway 2001:470:35:79b::1       # HE Tunnel Server IPv6 주소
```

설정 후 다시 한 번 재부팅(`sudo reboot`)하여 터널 인터페이스를 활성화합니다.

### 3. 무선 AP (Access Point) 설정

`hostapd`를 설치하여 라즈베리파이의 무선 랜카드가 Wi-Fi 신호를 송출하도록 만듭니다.

```bash
sudo apt-get install hostapd
sudo vi /etc/default/hostapd
```

```text
# 데몬 설정 파일 경로 지정
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
wpa_passphrase=1qaz2wsx  # Wi-Fi 비밀번호
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
```

```bash
sudo systemctl unmask hostapd
sudo systemctl start hostapd
```

### 4. DHCPv6 및 RA 설정 (dnsmasq)

AP에 접속한 클라이언트들에게 IPv6 주소(SLAAC)와 Google의 IPv6 DNS 정보를 할당해 주기 위해 `dnsmasq`를 설정합니다.

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
server=2001:4860:4860::8888
local=/kyle-rpi3/
domain=kyle-rpi3
dhcp-fqdn
enable-ra
dhcp-range=::,constructor:wlan0,slaac
dhcp-option=option6:dns-server,2001:4860:4860::8888
dhcp-authoritative
```

```bash
sudo systemctl restart dnsmasq
```

### 5. 포워딩 활성화 및 NAT6 라우팅 설정 (중요)

패킷이 유선 랜(`eth0`), 무선 랜(`wlan0`), 그리고 터널(`he-ipv6`) 사이를 자유롭게 넘나들 수 있도록 커널 포워딩을 켭니다.

```bash
sudo vi /etc/sysctl.conf
```

```text
net.ipv4.ip_forward=1
net.ipv6.conf.all.forwarding=1
```

```bash
sudo sysctl -p
sudo apt-get install iptables
```

#### 부팅 시 수동 실행 명령어 (라우팅 복구 및 ip6tables 설정)

터널링 인터페이스가 올라오면서 기존 IPv4 기본 라우팅 경로가 꼬일 수 있으므로 이를 바로잡고, 내부망 기기들이 외부 IPv6망으로 나갈 수 있도록 **MASQUERADE(NAT)** 처리를 해주는 필수 명령어들입니다.

부팅 후 1회 수동으로 실행해 주어야 합니다.

```bash
# 1. 기존 기본 라우트 삭제 및 eth0 기반으로 재설정
sudo ip route del default
sudo ip route add default via 192.168.0.1 dev eth0

# 2. DNS 요청(UDP 53)을 Google IPv6 DNS로 강제 포워딩 (DNAT/SNAT)
sudo ip6tables -t nat -A PREROUTING -i wlan0 -p udp --dport 53 -j DNAT --to-destination 2001:4860:4860::8888
sudo ip6tables -t nat -A POSTROUTING -o he-ipv6 -p udp --dport 53 -j SNAT --to-source 2001:470:35:79b::2

# 3. 내부망에서 터널을 통해 나가는 트래픽에 대한 NAT 처리
sudo ip6tables -t nat -A POSTROUTING -o he-ipv6 -j MASQUERADE
```

### Bonus: 원격 트래픽 실시간 캡처 (tcpdump + Wireshark)

트래픽이 터널을 통해 정상적으로 변환되어 나가는지 확인하려면 권한 설정을 통해 로컬 PC에서 실시간 패킷 캡처를 진행해 보세요.

```bash
# 패키지 설치 및 pcap 그룹 권한 부여
sudo apt-get install tcpdump
sudo groupadd pcap
sudo usermod -a -G pcap rex2864
sudo chgrp pcap /usr/bin/tcpdump
sudo chmod 750 /usr/bin/tcpdump
sudo setcap cap_net_raw,cap_net_admin=eip /usr/bin/tcpdump
```

Windows PC 터미널(CMD)에서 아래 명령어를 실행하면 Wireshark를 통해 실시간 분석이 가능합니다.

```cmd
ssh rex2864@192.168.1.10 tcpdump -i any -U -s0 -w - 'not port 22' | "c:\Program Files\Wireshark\Wireshark.exe" -k -i -
```

---

Date: 2026. 03. 16

Tags: RaspberryPi, IPv6, TunnelBroker, HurricaneElectric, 무선AP설정, 네트워크라우팅, iptables, NAT6, 서버관리
