## 터미널(CLI) 환경에서 Wi-Fi 연결하기 (wpa_supplicant)

(gemini로 작성됨)

데스크톱 환경(GUI)이 없는 리눅스 서버나 최소 설치 환경에서
무선 인터넷(Wi-Fi)을 연결해야 할 때가 있습니다. 이 글에서는
`wpa_supplicant`를 활용하여 터미널 명령어만으로 Wi-Fi에
연결하는 방법을 단계별로 알아보겠습니다.

> **💡 참고 사항**
> * 모든 작업은 **root 권한** (`sudo -i` 또는 명령어 앞에 `sudo` 사용)으로 진행해야 합니다.
> * 이 글에서는 무선 네트워크 인터페이스 이름을 `wlp2s0b1`로 가정합니다. 본인 PC의 인터페이스 이름은 `ip link` 또는 `iw dev` 명령어로 미리 확인해 주세요.

### 1. 주변 Wi-Fi(AP) 검색 및 동작 확인

먼저 무선 랜카드가 정상적으로 동작하는지, 그리고 연결하려는 Wi-Fi 신호(AP)가 잘 잡히는지 확인합니다.

```bash
iw wlp2s0b1 scan
```

명령어를 입력하면 주변의 다양한 무선 네트워크 정보가 출력됩니다. 연결하고자 하는 Wi-Fi의 이름(SSID)이 목록에 있는지 확인합니다.

### 2. 연결 설정 파일(wpa_supplicant.conf) 생성

연결할 Wi-Fi의 이름(ESSID)과 비밀번호(Passphrase)를 암호화하여
설정 파일에 저장합니다. `wpa_passphrase` 명령어를 사용하면
비밀번호를 해시(Hash) 값으로 변환하여 안전하게 저장할 수 있습니다.

```bash
# ESSID에 와이파이 이름, passphrase에 비밀번호를 입력하세요.
wpa_passphrase ESSID passphrase | tee -a /etc/wpa_supplicant/wpa_supplicant.conf
```

#### 🔒 보안 팁 (선택 사항)

생성된 `/etc/wpa_supplicant/wpa_supplicant.conf` 파일을 `vi`나
`nano` 편집기로 열어보면, 본인이 입력한 원래 비밀번호가
주석(`#`)으로 남아있습니다. 보안을 위해 해당 줄은 삭제하는 것을
권장합니다.

### 3. 숨겨진 와이파이(Hidden SSID)를 위한 추가 설정

만약 연결하려는 Wi-Fi가 이름이 숨겨져 있는 **Hidden SSID**라면, 설정 파일에 한 줄을 더 추가해야 정상적으로 연결할 수 있습니다.

설정 파일(`/etc/wpa_supplicant/wpa_supplicant.conf`)을 편집기로 열고, `network={ ... }` 블록 안에 `scan_ssid=1` 항목을 추가해 줍니다.

```text
network={
    ssid="ESSID"
    scan_ssid=1
    #psk="passphrase" (이 줄은 삭제 권장)
    psk=생성된_긴_암호화_키
}
```

### 4. 네트워크 인터페이스 파일에 등록

마지막으로, 시스템이 부팅되거나 무선 랜카드가 인식될 때
자동으로 위에서 만든 설정을 사용해 IP를 할당받도록(DHCP)
설정해야 합니다.

`/etc/network/interfaces` 파일을 열고 아래 내용을 추가합니다.

```text
allow-hotplug wlp2s0b1
iface wlp2s0b1 inet dhcp
    wpa-conf /etc/wpa_supplicant/wpa_supplicant.conf
```

* `allow-hotplug`: 장치가 연결될 때 인터페이스를 자동으로 활성화합니다.
* `inet dhcp`: 공유기로부터 자동으로 IP 주소를 할당받습니다.

### 5. 변경 사항 적용 (네트워크 재시작)

모든 설정이 완료되었습니다! 이제 네트워크 인터페이스를 재시작하여 Wi-Fi에 연결해 봅시다.

```bash
ifdown wlp2s0b1 && ifup wlp2s0b1
```

또는 시스템에 따라 아래 명령어로 네트워크 서비스를 재시작할 수도 있습니다.

```bash
systemctl restart networking
```

이제 `ping google.com` 등의 명령어를 통해 인터넷이 정상적으로 연결되었는지 테스트해 보세요!

### 🚨 트러블슈팅 (자주 발생하는 에러 및 해결 방법)

설정을 마쳤는데도 Wi-Fi 연결이 되지 않는다면 아래의 항목들을 순서대로 점검해 보세요.

#### 1. 무선 인터페이스 이름이 다르거나 찾을 수 없는 경우

우분투, 데비안, 알파인 리눅스(Alpine Linux) 등 사용하는 OS 환경이나
하드웨어에 따라 `wlp2s0b1`이 아닌 `wlan0`과 같은 다른 이름을 사용할
수 있습니다.

**해결 방법:** 아래 명령어로 현재 시스템의 정확한 네트워크 장치
이름을 먼저 확인한 뒤, 위 설정 과정의 이름들을 모두 본인의 인터페이스
이름으로 교체해 주세요.

```bash
ip link
# 또는
iw dev
```

#### 2. 설정은 마쳤는데 IP 주소를 받아오지 못하는 경우 (인터넷 안 됨)

`ifup` 명령어를 실행해도 공유기로부터 IP를 제대로 할당받지 못해 통신이 안 되는 경우가 있습니다.

**해결 방법:** DHCP 클라이언트를 수동으로 실행하여 진행 상황을 보거나 다시 IP 할당을 요청해 보세요.

```bash
dhclient -v wlp2s0b1
```

명령어 실행 후 `ip a` 명령어를 입력했을 때, 해당 인터페이스에 `inet 192.168.x.x` 형태의 IP 주소가 보인다면 성공입니다.

#### 3. 무선 랜카드 자체가 차단(Block)되어 있는 경우

간혹 하드웨어 스위치나 OS 설정에 의해 Wi-Fi 기능 자체가 잠겨있을 수
있습니다. (`RTNETLINK answers: Operation not possible due to RF-kill` 등의 에러 발생 시)

**해결 방법:** `rfkill` 명령어로 차단 여부를 확인하고 소프트웨어 차단을 해제합니다.

```bash
rfkill list all
rfkill unblock wifi
```

#### 4. 설정 변경 후 프로세스가 꼬인 경우

설정 파일을 여러 번 수정하면서 네트워크를 껐다 켜다 보면,
기존에 실행된 `wpa_supplicant` 백그라운드 프로세스와 충돌이
발생할 수 있습니다.

**해결 방법:** 실행 중인 관련 프로세스를 강제로 종료한 뒤 네트워크 인터페이스를 다시 시작해 보세요.

```bash
killall wpa_supplicant
ifdown wlp2s0b1 && ifup wlp2s0b1
```

---

Date: 2026. 03. 15

Tags: Linux, Ubuntu, Debian, 네트워크설정, CLI, wpasupplicant, 와이파이연결, 라즈베리파이, 서버관리
