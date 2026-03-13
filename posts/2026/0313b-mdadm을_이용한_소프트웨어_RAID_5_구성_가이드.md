## mdadm을 이용한 소프트웨어 RAID 5 구성 가이드

(gemini로 작성됨)

여러 개의 하드디스크를 하나로 묶어 성능과 안정성을 높이는
**RAID(Redundant Array of Independent Disks)**는 서버 운영의
필수 요소입니다. 이번 포스팅에서는 Ubuntu/Debian 계열 리눅스에서
mdadm 도구를 사용하여 RAID 5를 구성하는 방법을 단계별로 알아보겠습니다.

1. mdadm 설치 및 디스크 준비

먼저 RAID 관리 도구인 mdadm을 설치하고, RAID에 사용할 디스크의 파티션을 설정합니다.

```bash
# mdadm 설치
$ sudo apt install mdadm

# 디스크 파티션 설정 (예: /dev/sdb)
$ sudo fdisk /dev/sdb
```

 * fdisk 내부 작업:
   * n: 새로운 파티션 생성 (모든 설정은 기본값으로 진행)
   * t: 파티션 타입 변경
   * fd: Linux raid autodetect 타입 선택
   * w: 설정 저장 및 종료

> 참고: RAID에 포함될 모든 디스크(/dev/sdc, /dev/sdd, /dev/sde 등)에 위 작업을 동일하게 반복합니다.

2. RAID 5 배열 생성

준비된 4개의 디스크 파티션을 사용하여 /dev/md0라는 이름의 RAID 5 배열을 생성합니다.

```bash
# RAID 5 생성 (디스크 4개 사용)
$ sudo mdadm --create /dev/md0 --level=5 --raid-devices=4 /dev/sdb1 /dev/sdc1 /dev/sdd1 /dev/sde1
```

3. 파일 시스템 구축 및 마운트

생성된 RAID 장치를 포맷하고 시스템에 연결(마운트)합니다.

```bash
# ext4 파일 시스템으로 포맷
$ sudo mkfs.ext4 /dev/md0

# 마운트 포인트 생성 및 마운트
$ sudo mkdir -p /mnt/data
$ sudo mount /dev/md0 /mnt/data
```

4. 구성 정보 저장 및 영구 설정

재부팅 후에도 RAID 구성이 유지되도록 설정 파일을 업데이트해야 합니다.
이 과정이 없으면 재부팅 시 RAID 장치명이 변경되거나 마운트에 실패할 수 있습니다.

RAID 정보 스캔 및 설정 파일 등록

```bash
# RAID 상세 정보 확인 (여기서 나온 UUID 확인)
$ sudo mdadm --detail --scan

# mdadm.conf에 설정 추가
$ sudo echo "ARRAY /dev/md0 metadata=1.2 UUID=[확인된_UUID]" >> /etc/mdadm/mdadm.conf

# 부팅 시 RAID를 인식할 수 있도록 초기 램 디스크 업데이트
$ sudo update-initramfs -u
```

자동 마운트 설정 (fstab)

```bash
# /etc/fstab에 추가하여 부팅 시 자동 마운트
$ sudo echo "/dev/md0 /mnt/data ext4 defaults 0 0" >> /etc/fstab

# 시스템 설정 반영 및 재부팅
$ sudo systemctl daemon-reload
$ sudo reboot
```

5. 상태 확인 (Tip)

RAID가 정상적으로 동작하는지 확인하려면 다음 명령어를 사용하세요.

```bash
$ sudo mdadm --detail /dev/md0
```

State : clean 또는 active 메시지가 보인다면 성공적으로 구축된 것입니다!

---

Date: 2026. 03. 13

Tags: Linux, Ubuntu, RAID, RAID5, mdadm, Storage, Server, SysAdmin, 리눅스, 서버관리
