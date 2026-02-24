## backup with wol(wakeonlan)

backup 자동화를 위해서 WOL과 backup script를 활용하는 방법을 정리한다.

backup을 위한 machine이 별도로 구축되어 있고, LAN으로 연결이 되어 있어야 한다.

running system/machine에서 crontab이나 scheduler를 활용하여 일정 시간이 되면 WOL로 backup machine을 깨우고

backup machine에서는 bootup이 끝나면 또는 일정 시간이 되면 backup script를 실행하는 구조이다.


### WakeOnLan 관련 설정 in BIOS

Power Management 또는 Advanced 탭으로 이동하여 "Wake on LAN", "Power On By PCI-E" 또는 "Resume by LAN" 등으로 찾아보고 enabled로 변경하도록 하자.

"ErP Ready" 항목이 있다면 반드시 disabled로 설정하도록 하자. 이 기능이 켜져 있으면 대기 전력을 차단하여 WakeOnLan이 동작할 수 없다.


### WakeOnLan 설정 for Linux

ethtool을 사용한다. package manager를 통해서 미리 설치해 두도록 하자.

```bash 
sudo apt install ethtool
```

ethernet interface가 enp3s0라고 가정한다.

먼저 ethernet interface의 현재 설정 상태를 확인한다.

```bash
ckadm@mintp ~ $ sudo ethtool enp3s0 | grep Wake
    Supports Wake-on: pumbg
    Wake-on: d
```

"Wake-on: d"에서 "d"는 disabled를 의미한다. 이것을 "g" (granted)로 바꿔야 한다. 아래 명령으로 변경하도록 하자.

```bash
ckadm@mintp ~ $ sudo ethtool -s enp3s0 wol g
```

다시 설정 상태 확인을 하면...

```bash
ckadm@mintp ~ $ sudo ethtool enp3s0 | grep Wake
    Supports Wake-on: pumbg
    Wake-on: g
```


Linux command line tool로 `wakonlan`이 있다. package manager로 설치할 수 있다.

```bash
sudo apt install wakeonlan
```

사용법은 아래와 같이 target machine/device의 MAC address를 입력해주면 된다.

```bash
wakeonlan AA:BB:CC:DD:EE:FF
```


### WakeOnLan 설정 for Windows

#### Windows 장치 관리자 설정

1. 시작 버튼 우클릭 -> 장치 관리자를 엽니다.
2. 네트워크 어댑터 항목에서 실제 사용 중인 유선 랜카드(Ethernet Controller)를 찾아 우클릭 -> 속성을 누릅니다.
3. 전원 관리 탭:
  * 이 장치를 사용하여 컴퓨터의 대기 모드를 종료할 수 있음 체크
  * 매직 패킷에서만 컴퓨터의 대기 모드를 종료할 수 있음 체크
4. 고급 탭:
  * 속성 목록에서 Wake on Magic Packet (매직 패킷 웨이크 업)을 찾아 값을 Enabled (사용)으로 설정합니다.
  * 절전형 이더넷 또는 Energy Efficient Ethernet은 가급적 Disabled (사용 안 함)로 하는 것이 안정적입니다.

#### 빠른 시작 켜기 비활성화

Windows의 '빠른 시작' 기능은 PC를 완전히 종료하지 않고 하이브리드 절전 상태로 만들기 때문에 WoL 작동을 방해할 수 있습니다.

1. 제어판 -> 전원 옵션 -> 전원 단추 작동 설정으로 이동합니다.
2. 현재 사용할 수 없는 설정 변경을 클릭합니다.
3. 아래쪽 종료 설정에서 빠른 시작 켜기(권장) 체크를 해제하고 변경 내용을 저장합니다.

#### WOL powershell script

target device/machine의 MAC address를 `$Mac`에 설정해야한다.

```powershell
$Mac = "AA:BB:CC:DD:EE:FF"
$MacByteArray = $Mac -split "[:-]" | ForEach-Object { [Byte] "0x$_"}
[Byte[]] $MagicPacket = (,0xFF * 6) + ($MacByteArray  * 16)
$UdpClient = New-Object System.Net.Sockets.UdpClient
$UdpClient.Connect(([System.Net.IPAddress]::Broadcast),7)
$UdpClient.Send($MagicPacket,$MagicPacket.Length)
$UdpClient.Close()
```

### backup script for linux

먼저 CIFS(samba) mount를 해서 source machine과 연결한다.

이후 rsync로 source와 target을 sync 시킨다.

완료된 이후 일정 시간(여기서는 10초) 이후 machine을 shutdown 시킨다.

```bash
#!/bin/sh

if grep -qs " /path/source " /proc/mounts; then
    echo "already mounted"
else
    sudo mount -t cifs -o credentials=/mnt/credential //source_IP/source_dir /path/source
fi
rsync -avh /path/source/ /path/target/
sync
sleep 10
sudo shutdown now
```

### backup script for windows

windows에서는 network drive 연결을 활용하고, rsync 대신 robocopy를 사용한다.

```powershell
@echo off

net use x: \\source_IP\source_dir "PASSWORD" /user:USERID

set YYYYMMDD=%DATE:~0,4%%DATE:~5,2%%DATE:~8,2%
set HHMMSS=%TIME:~0,2%%TIME:~3,2%%TIME:~6,2%

robocopy X:\ D:\ /MIR /LOG+:"C:\path\to\logging\%YYYYMMDD%-%HHMMSS%.log"

net use x: /delete

shutdown /s /f /t 0
```

---

Date: 2026. 02. 24

Tags: backup, wol, wakeonlan, rsync, robocopy
