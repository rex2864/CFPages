## GDB 디버깅 기초부터 원격디버깅, core dump 분석까지

(gemini로 작성함)


안드로이드 임베디드 개발에서 `Segmentation Fault`는 피할 수 없는 숙명과 같습니다.
터미널 기반의 GDB도 강력하지만, 시각적인 **VS Code GUI**와 결합하면 생산성이 극대화됩니다.
기초 명령어부터 안드로이드 원격 디버깅, 그리고 VS Code 자동화 설정까지 한 번에 정리합니다.


### 1. GDB 기초 명령어 (Cheatsheet)

디버깅의 기본은 상태 확인과 흐름 제어입니다.

| 명령어             | 단축키    | 설명                                        |
|--------------------|-----------|---------------------------------------------|
| **break**          | `b`       | 중단점 설정 (예: `b main`, `b 15`)          |
| **run / continue** | `r` / `c` | 실행 시작 / 다음 중단점까지 계속            |
| **next / step**    | `n` / `s` | 한 줄 실행 (함수 건너뛰기 / 함수 내부 진입) |
| **print**          | `p`       | 변수 값 확인 (예: `p var`)                  |
| **backtrace**      | `bt`      | **(필수)** 크래시 발생 시 호출 스택 확인    |
| **watch**          | `watch`   | 변수 값이 변경될 때 자동 중단               |


### 2. 안드로이드 원격 디버깅 환경 구축

Target(보드)과 Host(PC) 사이의 연결 고리를 만드는 과정입니다.

#### Step 1. Target(보드) 설정

보드에서 `gdbserver`를 실행하여 PC의 접속을 기다립니다.

```bash
# 1234 포트로 실행 중인 프로세스(PID)에 attach
gdbserver :1234 --attach [PID]
```

#### Step 2. Host(PC) 포트 포워딩

USB로 연결된 경우, ADB를 통해 네트워크 터널을 뚫어줍니다.

```bash
adb forward tcp:1234 tcp:1234
```


### 3. VS Code 연동 설정 (Visual Debugging)

터미널에 명령어를 치는 대신, VS Code의 F5 키로 디버깅을 시작하는 설정입니다.
프로젝트 루트의 `.vscode/launch.json` 파일을 다음과 같이 작성합니다.

#### `launch.json` 설정 예시

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Android GDB Remote",
            "type": "cppdbg",
            "request": "launch",
            // 빌드된 바이너리 경로 (Symbol 정보가 포함된 unstripped 파일)
            "program": "${workspaceFolder}/out/target/product/[보드명]/symbols/system/bin/my_app",
            "miDebuggerServerAddress": "localhost:1234",
            "miDebuggerPath": "/path/to/android-ndk/prebuilt/linux-x86_64/bin/gdb",
            "stopAtEntry": false,
            "cwd": "${workspaceFolder}",
            "externalConsole": false,
            "MIMode": "gdb",
            "setupCommands": [
                {
                    "description": "ARM 아키텍처 설정",
                    "text": "set architecture arm64",
                    "ignoreFailures": false
                },
                {
                    "description": "공유 라이브러리 심볼 경로 설정",
                    "text": "set solib-search-path ${workspaceFolder}/out/target/product/[보드명]/symbols/system/lib64",
                    "ignoreFailures": true
                }
            ]
        }
    ]
}
```

**중요** : `${workspaceFolder}`가 포함된 항목 등 경로가 필요한 경우는 반드시 프로젝트 설정에 맞도록 수정되어야 함.


### 4. Core Dump 분석법 (사후 분석)

실시간 연결이 어려울 때, 죽은 시점의 메모리 파일을 가져와 분석하는 방법입니다.

1. **덤프 활성화:** `adb shell "ulimit -c unlimited"`
2. **파일 가져오기:** `adb pull /data/local/tmp/core.xxx ./`
3. **VS Code 설정:** 위 `launch.json`에서 `request`를 `"launch"` 대신 `"attach"`로 바꾸고 `coreDumpPath` 속성을 추가하거나, 터미널에서 직접 실행합니다.

```bash
gdb-multiarch ./my_app_unstripped ./core.xxx
```


### 5. 실무자를 위한 핵심 체크리스트 (Troubleshooting)

* **함수 이름이 `??`로 보인다면?**
  * `solib-search-path`가 정확한지 확인하세요. 안드로이드 빌드 결과물 중 `symbols` 폴더 내의 라이브러리 경로여야 합니다.
* **파일이 Stripped 되었나요?**
  * Target 보드에 올라가는 파일은 용량 최적화를 위해 심볼이 제거된(stripped) 상태입니다. GDB를 실행할 때는 반드시 **빌드 서버에 남은 용량이 큰 바이너리**를 지정해야 합니다.
* **권한 문제**
  * 시스템 프로세스를 디버깅할 때는 반드시 `adb root` 상태여야 `gdbserver`가 정상적으로 동작합니다.


### 마치며

GDB는 단순한 도구를 넘어 시스템 내부를 들여다보는 창과 같습니다.
특히 VS Code TUI 모드(`Ctrl+X, A`)나 GUI 연동을 적절히 혼합하면,
복잡한 커널/프레임워크 에러도 충분히 정복할 수 있습니다.
오늘 정리한 `launch.json` 템플릿을 복사해서 여러분의 환경에 맞춰 사용해 보세요!

---

Date: 2026. 02. 15

Tags: gdb, debugging, remote_debugging, coredump, vscode
