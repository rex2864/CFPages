## tcpdump 완벽 가이드: 기본 사용법부터 패킷 캡처 예제까지

(gemini로 작성됨)

리눅스 서버에서 네트워크 장애가 발생하거나 특정 패킷의 흐름을 분석해야 할 때, 가장 먼저 찾게 되는 강력한 툴이 바로 **`tcpdump`**입니다. 명령줄(CLI) 환경에서 네트워크 인터페이스를 거치는 패킷을 가로채고 분석할 수 있게 해줍니다.

이번 글에서는 `tcpdump`의 기본 구문부터, 실무에서 가장 많이 쓰이는 필터링 예제들을 상황별로 정리해 보겠습니다.

### 1. tcpdump 기본 구문

`tcpdump`는 수많은 옵션을 제공합니다. 전체 명령어 구조는 아래와 같습니다.

```bash
# tcpdump [ -AdDefIKlLnNOpqRStuUvxX ][ -B buffer_size ][ -c count ][ -C file_size ][ -G rotate_seconds ][ -F file ][ -i interface ][ -m module ][ -M secret ][ -r file ][ -s snaplen ][ -T type ][ -w file ][ -W filecount ][ -E spi@ipaddr algo:secret,... ][ -y datalinktype ][ -z postrotate-command ][ -Z user ]
```

> 너무 복잡해 보이지만, 실제로는 아래의 예제들처럼 필요한 옵션 몇 가지만 조합해서 사용하는 경우가 대부분입니다.

### 2. 필수 기본 옵션 (인터페이스, 파일 저장, 개수 제한)

가장 기본적으로 패킷을 어디서 수집하고, 어떻게 저장할지 결정하는 옵션들입니다.

**특정 네트워크 인터페이스 패킷 보기 (`-i`)**

```bash
tcpdump -i eth0
```

**수집할 패킷 개수 제한하기 (`-c`)**

```bash
# 카운터 10개만 캡처하고 종료
tcpdump -i eth0 -c 10
```

**캡처 결과를 파일로 저장하기 (`-w`)**

텍스트가 아닌 바이너리(pcap) 형식으로 저장되며, 나중에 Wireshark 같은 분석 도구로 열어볼 수 있습니다.

```bash
tcpdump -w tcpdump.log
```

**저장된 패킷 캡처 파일 읽기 (`-r`)**

```bash
tcpdump -r tcpdump.log
```

### 3. IP 및 네트워크 대역 필터링

특정 출발지(Source)나 목적지(Destination)의 IP를 지정하여 패킷을 걸러냅니다.

**특정 Host(IP) 양방향 패킷 캡처**

해당 IP로 들어오거나 나가는 모든 패킷을 보여줍니다.

```bash
tcpdump host 192.168.0.1
```

**출발지(Source) IP 지정**

```bash
tcpdump -i eth0 src 192.168.0.1
```

**목적지(Destination) IP 지정**

```bash
tcpdump -i eth0 dst 192.168.0.1
```

**CIDR 포맷으로 서브넷 대역 지정**

특정 IP 대역 전체를 캡처할 때 유용합니다.

```bash
tcpdump net 192.168.0.1/24
```

### 4. 프로토콜 및 포트(Port) 필터링

TCP/UDP 등 특정 프로토콜이나 포트 번호만을 타겟팅합니다.

**특정 프로토콜만 캡처**

```bash
tcpdump tcp
tcpdump udp
```

**특정 포트 양방향 캡처**

```bash
tcpdump port 3389
tcpdump -i eth0 tcp port 80
```

**출발지 / 목적지 포트 지정**

```bash
tcpdump src port 3389
tcpdump dst port 3389
```

### 5. 논리 연산자를 활용한 조건 조합 (핵심)

`tcpdump`의 진가는 여러 조건을 조합할 때 나타납니다. **`and (&&)`**, **`or (||)`**, **`not (!)`** 을 사용하여 복잡한 필터를 구성할 수 있습니다.

**AND 연산: 두 조건을 모두 만족하는 패킷**

```bash
# 출발지 IP가 192.168.0.1 이면서 TCP 포트가 80인 패킷
tcpdump -i eth0 src 192.168.0.1 and tcp port 80

# UDP 프로토콜이면서 출발지 포트가 53(DNS)인 패킷
tcpdump udp and src port 53
```

**NOT 연산: 특정 조건 제외**

```bash
# 출발지 IP가 x.x.x.x 이고, 목적지 포트가 22(SSH)가 아닌 패킷
tcpdump src x.x.x.x and not dst port 22
```

**Grouping (괄호 사용): 복잡한 조합**

괄호를 사용할 때는 반드시 명령어 전체나 괄호 부분을 작은따옴표(`' '`)로 감싸주어야 쉘(Shell)에서 특수문자로 오작동하지 않습니다.

```bash
# 출발지 IP가 x.x.x.x 이고, 목적지 포트가 3389 또는 22인 패킷
tcpdump 'src x.x.x.x and (dst port 3389 or 22)'
```

---

Date: 2026. 03. 16

Tags: Linux, tcpdump, 네트워크, 패킷분석, 트러블슈팅, 서버관리, 네트워크보안, CLI
