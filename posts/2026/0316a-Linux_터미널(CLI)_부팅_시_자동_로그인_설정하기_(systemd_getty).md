## Linux 터미널(CLI) 부팅 시 자동 로그인 설정하기 (systemd getty)

(gemini로 작성됨)

데스크톱 환경(GUI)이 없는 리눅스 서버나 개인용 소형 기기를 세팅할 때, 부팅 완료 직후 터미널에 자동으로 로그인되도록 설정하고 싶을 때가 있습니다.

리눅스의 시스템 및 서비스 관리자인 `systemd` 환경에서는 `getty@.service` 파일을 수정하여 이 기능을 쉽게 구현할 수 있습니다. 기존 시스템 파일을 직접 건드리지 않고 안전하게 설정을 덮어쓰는(Override) 방법을 알아보겠습니다.

### 1. getty 서비스 설정 파일 열기

터미널에 아래 명령어를 입력하여 `getty@.service`의 설정을 덮어쓸 수 있는 편집 창을 엽니다.

```bash
sudo systemctl edit getty@.service
```

> **왜 `edit` 명령어를 사용하나요?**
> 원본 서비스 파일(`/usr/lib/systemd/system/getty@.service`)을 직접 수정하면 패키지 업데이트 시 설정이 초기화될 위험이 있습니다. `systemctl edit`을 사용하면 `/etc/systemd/system/` 경로에 안전하게 사용자 정의(Override) 설정 파일만 따로 생성할 수 있습니다.

### 2. 자동 로그인 설정 추가하기

편집기가 열리면 아래의 내용을 빈 공간에 작성해 줍니다. `[ID]` 부분에는 자동 로그인할 **실제 사용자 계정명**(예: `root` 또는 `ubuntu` 등)을 적어주세요.

```ini
[Service]
ExecStart=
ExecStart=-/sbin/agetty --noclear --autologin [ID] %I $TERM
```

#### 핵심 포인트: `ExecStart=`를 두 번 적는 이유

위 코드를 보면 `ExecStart` 항목이 두 번 연달아 작성되어 있습니다. 여기에는 아주 중요한 `systemd`의 작동 원리가 숨어있습니다.

1. **`ExecStart=` (빈 값)**: 첫 번째 빈 `ExecStart`는 원본 서비스 파일에 설정되어 있던 **기존 실행 명령어를 초기화(Clear)**하는 역할을 합니다.
2. **`ExecStart=-/sbin/agetty ...`**: 기존 명령어가 지워진 상태에서, 두 번째 줄에 작성한 자동 로그인(`--autologin`) 옵션이 포함된 **새로운 명령어를 실제 작동할 명령어로 등록**하게 됩니다.

만약 첫 번째 빈 줄을 넣지 않고 바로 두 번째 줄만 적는다면, `systemd`는 "하나의 서비스에 실행 명령어가 여러 개 중복되어 있다"라고 판단하여 에러를 발생시키고 서비스가 실행되지 않습니다.

### 3. 설정 적용 및 재부팅

파일을 저장하고 편집기를 종료한 뒤, 변경된 `systemd` 설정을 시스템에 다시 불러옵니다.

```bash
sudo systemctl daemon-reload
```

이제 시스템을 재부팅(`sudo reboot`) 해보면, 로그인 프롬프트를 거치지 않고 지정한 계정으로 즉시 로그인되는 것을 확인할 수 있습니다!

---

Date: 2026. 03. 16

Tags: Linux, systemd, getty, 자동로그인, autologin, 서버관리, 리눅스팁, CLI
