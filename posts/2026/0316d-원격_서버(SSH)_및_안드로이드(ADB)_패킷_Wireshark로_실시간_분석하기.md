## 원격 서버(SSH) 및 안드로이드(ADB) 패킷 Wireshark로 실시간 분석하기

(gemini로 작성됨)

보통 원격 리눅스 서버에서 네트워크 장애를 분석할 때 `tcpdump`로 `.pcap` 파일을 저장하고, 이를 FTP나 SCP로 로컬 PC에 다운로드한 뒤 Wireshark로 열어보는 방식을 많이 사용합니다. 하지만 이 방식은 번거롭고 실시간 트래픽 흐름을 파악하기 어렵습니다.

이번 글에서는 **원격 서버(SSH)나 안드로이드 기기(ADB)에서 캡처되는 패킷을 내 PC의 Wireshark 화면으로 실시간 전송하여 분석하는 방법**을 알아보겠습니다.

> **필수 전제 조건**
> * 로컬 PC(Windows)에 Wireshark가 기본 경로(`C:\Program Files\Wireshark\Wireshark.exe`)에 설치되어 있어야 합니다.
> * 원격 기기(Linux 서버, 안드로이드 등)에는 `tcpdump`가 설치되어 있어야 하며, root 권한이 필요할 수 있습니다.

### 1. 기본 SSH를 이용한 실시간 패킷 캡처

Windows 10/11이나 macOS 등 기본적으로 `ssh` 클라이언트가 설치된 환경에서 가장 간편하게 사용할 수 있는 방법입니다. 원격 서버의 터미널 출력을 파이프(`|`)를 통해 로컬의 Wireshark로 넘겨줍니다.

```cmd
# 예시 1: root 계정으로 접속하여 l2tpeth0 인터페이스 캡처
ssh root@192.168.1.4 /usr/sbin/tcpdump -i l2tpeth0 -U -s0 -w - 'not port 22' | "c:\Program Files\Wireshark\Wireshark.exe" -k -i -

# 예시 2: 일반 계정으로 접속하여 wlan0 인터페이스 캡처
ssh rex2864@192.168.1.10 /usr/bin/tcpdump -i wlan0 -U -s0 -w - 'not port 22' | "c:\Program Files\Wireshark\Wireshark.exe" -k -i -
```

#### 명령어 옵션 파헤치기

**`tcpdump` 옵션:**
* `-U` : 패킷이 버퍼에 쌓이기를 기다리지 않고 즉시 출력합니다. (실시간 분석을 위한 핵심 옵션)
* `-s0` (또는 `-s 0`) : 패킷의 길이를 자르지 않고 전체 크기(Snaplen)를 캡처합니다.
* `-w -` : 캡처한 데이터를 파일로 저장하지 않고 표준 출력(stdout)으로 내보냅니다.
* **`'not port 22'`** : ⭐ 매우 중요합니다! SSH 통신 자체의 패킷을 제외하지 않으면, 캡처된 데이터를 로컬로 보내는 트래픽이 다시 캡처되는 **무한 루프(Feedback Loop)**에 빠지게 됩니다.

**`Wireshark.exe` 옵션:**
* `-k` : 프로그램 실행과 동시에 즉시 캡처를 시작합니다.
* `-i -` : 표준 입력(stdin)으로 들어오는 데이터를 캡처 인터페이스로 사용합니다.

### 2. Plink(PuTTY)를 활용한 SSH 및 우회(Jump) 접속 캡처

PuTTY에 포함된 CLI 도구인 `plink.exe`를 사용한 방법입니다. 특히 두 번째 예시처럼 **중간 서버(Jump Host)를 거쳐서 내부망에 있는 다른 서버의 패킷을 캡처**해야 할 때 매우 유용합니다.

```cmd
# 기본 plink를 이용한 캡처
plink.exe -ssh root@192.168.1.4 "/usr/sbin/tcpdump -i eth0 -s 0 -U -w - 'not port 22'" | "c:\Program Files\Wireshark\Wireshark.exe" -k -i -

# 중간 서버(192.168.1.4)를 거쳐 내부망 서버(192.168.0.2)의 vlan0 인터페이스 캡처
plink.exe -ssh root@192.168.1.4 "ssh -q -o StrictHostKeyChecking=no root@192.168.0.2 /usr/sbin/tcpdump -i vlan0 -s 0 -U -w - 'not port 22'" | "c:\Program Files\Wireshark\Wireshark.exe" -k -i -
```

* 중간 서버를 거칠 때는 캡처 대상 서버의 SSH 인증 키 경고(`StrictHostKeyChecking=no`)나 불필요한 메시지(`-q`)를 억제해야 Wireshark가 데이터를 pcap 포맷으로 정상 인식할 수 있습니다.

### 3. ADB를 이용한 안드로이드(Android) 단말기 캡처

안드로이드 앱 개발이나 모바일 네트워크 환경을 분석할 때 활용하는 방법입니다. 단말기가 PC에 USB로 연결되어 있고, 디버깅 모드가 켜져 있어야 합니다.

```cmd
adb exec-out "tcpdump -i usb0.4 -s 0 -U -w - 2> /dev/null" | "c:\Program Files\Wireshark\Wireshark.exe" -k -i -
```

* **`adb exec-out`** : 기존 `adb shell`과 달리 바이너리 데이터를 손상 없이 그대로 출력해 주는 명령어입니다.
* **`2> /dev/null`** : `tcpdump`가 실행되면서 화면에 찍는 텍스트 로그(stderr)를 제거합니다. 이 텍스트가 파이프를 타고 넘어가면 Wireshark가 파일 포맷 오류를 일으킬 수 있으므로 반드시 필요합니다.

위 명령어들을 배치 파일(`.bat` 또는 `.cmd`)로 만들어 바탕화면에 두고 사용하시면, 클릭 한 번으로 원격 서버의 실시간 패킷 창을 띄울 수 있어 업무 효율이 크게 올라갑니다!

---

Date: 2026. 03. 16

Tags: Wireshark, tcpdump, SSH, ADB, 네트워크분석, 패킷캡처, 트러블슈팅, 서버관리, 안드로이드개발
