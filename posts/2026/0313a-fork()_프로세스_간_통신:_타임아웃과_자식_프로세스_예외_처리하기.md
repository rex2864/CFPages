## fork() 프로세스 간 통신: 타임아웃과 자식 프로세스 예외 처리하기

(gemini로 작성됨)

리눅스 시스템 프로그래밍에서 `fork()`를 이용해 자식 프로세스를 생성하고
파이프(Pipe)로 데이터를 주고받는 패턴은 매우 흔합니다. 하지만 네트워크
소켓과 달리 일반적인 파일 디스크립터(FD) 기반의 파이프는 `read()` 호출
시 데이터가 올 때까지 무한정 대기(Blocking)하게 됩니다.

오늘은 `poll()`을 사용하여 **Blocking mode의 파이프에 타임아웃을 설정**하고,
**자식 프로세스의 Crash나 강제 종료 상황을 안전하게 처리**하는 방법을 알아보겠습니다.

### 1. 왜 `setsockopt`가 아닌 `poll()`인가?

소켓 통신에서는 `SO_RCVTIMEO` 옵션으로 타임아웃을 설정할 수 있지만,
파이프나 일반 FD에는 이 옵션을 사용할 수 없습니다. 따라서 **`poll()`**
시스템 콜을 사용하여 FD에 이벤트(데이터 수신, 연결 끊김 등)가 발생했는지
먼저 확인하는 과정이 필요합니다.

### 2. 핵심 시나리오

1. **정상 수신**: 자식이 제한 시간 내에 데이터를 보냄.
2. **타임아웃**: 자식이 너무 오래 걸려 부모가 기다리다 포기하고 자식을 종료시킴.
3. **자식 프로세스 Crash**: 자식이 데이터를 보내기 전 비정상 종료됨.

### 3. 통합 예제 코드

```cpp
#include <iostream>
#include <unistd.h>
#include <poll.h>
#include <sys/wait.h>
#include <signal.h>
#include <cstring>

int main() {
    int pipefd[2];
    if (pipe(pipefd) == -1) return 1;

    pid_t pid = fork();

    if (pid == 0) {
        // --- 자식 프로세스 영역 ---
        close(pipefd[0]); // 읽기 단 폐쇄

        // 상황에 따라 테스트 가능: 
        // 1. 정상: sleep(1);
        // 2. 타임아웃: sleep(10);
        // 3. 크래시: abort();
        sleep(5); 

        const char* msg = "Success";
        write(pipefd[1], msg, strlen(msg) + 1);
        close(pipefd[1]);
        return 0;

    } else {
        // --- 부모 프로세스 영역 ---
        close(pipefd[1]); // 쓰기 단 폐쇄

        struct pollfd pfd;
        pfd.fd = pipefd[0];
        pfd.events = POLLIN | POLLHUP | POLLERR; // 데이터 수신 및 끊김 감시

        // 3초 타임아웃 설정 (3000ms)
        int ret = poll(&pfd, 1, 3000);

        if (ret == 0) {
            // [Case 1] 타임아웃 발생
            std::cout << "[Parent] Timeout! 자식을 종료시킵니다." << std::endl;
            kill(pid, SIGTERM); // 자식에게 종료 신호 전송
        } 
        else if (ret > 0) {
            if (pfd.revents & (POLLHUP | POLLERR)) {
                // [Case 2] 자식 프로세스 비정상 종료 (파이프 닫힘)
                std::cout << "[Parent] 자식 프로세스가 응답 없이 종료되었습니다." << std::endl;
            } else if (pfd.revents & POLLIN) {
                // [Case 3] 정상 데이터 수신
                char buf[128];
                read(pipefd[0], buf, sizeof(buf));
                std::cout << "[Parent] 수신 데이터: " << buf << std::endl;
            }
        }

        // --- 사후 처리 (Zombie 프로세스 방지) ---
        int status;
        waitpid(pid, &status, 0); 
        
        if (WIFEXITED(status)) {
            std::cout << "[Parent] 자식 정상 종료 (Code: " << WEXITSTATUS(status) << ")" << std::endl;
        } else if (WIFSIGNALED(status)) {
            std::cout << "[Parent] 자식 시그널 종료 (Signal: " << WTERMSIG(status) << ")" << std::endl;
        }

        close(pipefd[0]);
        return 0;
    }
}

```

### 4. 주요 포인트 정리

#### 💡 `poll()`의 이벤트 마스크

* **`POLLIN`**: 읽을 데이터가 존재함.
* **`POLLHUP`**: 파이프의 쓰기 쪽이 닫힘 (자식 프로세스가 종료됨).
* **`POLLERR`**: 파일 디스크립터 에러 발생.

#### 💡 자식 프로세스 제어

* 부모가 타임아웃으로 먼저 탈출하더라도 자식은 시스템에 남아 '고아 프로세스'가 될 수 있습니다. **`kill(pid, SIGTERM)`**을 통해 명시적으로 종료해주는 것이 좋습니다.

#### 💡 좀비(Zombie) 방지

* 자식이 어떤 이유로 종료되었든 부모는 반드시 **`wait()`** 계열의 함수를 호출하여 자식의 종료 상태를 수거해야 리소스 누수를 막을 수 있습니다.

---

### 마무리

`fork()`와 파이프를 이용한 IPC 구현 시, `poll()`을 결합하면 훨씬 견고한 프로그램을 만들 수 있습니다.
특히 예외 상황(무한 대기, 프로세스 Crash)에 대응할 수 있는 코드는 실무 환경에서 필수적입니다.


## [추가 섹션] 대안: `timeout` 명령어로 간편하게 제어하기

직접 코드를 짜는 것이 가장 정교하지만, 단순히 외부 바이너리를 실행하고 시간 제한을 걸고 싶다면 리눅스 표준 도구인 `timeout` 명령어를 사용하는 것이 훨씬 경제적입니다.

### 1. CLI에서 직접 사용

```bash
# 3초 안에 안 끝나면 종료 (기본 SIGTERM)
$ timeout 3s ./my_program

# 3초 대기 후 응답 없으면 강제 종료 (SIGKILL)
$ timeout -k 1s 3s ./my_program

```

### 2. C/C++ 코드 내에서 `system()`이나 `popen()`과 조합

프로그램 내부 로직이 복잡하지 않다면, 직접 `fork/exec`를 구현하는 대신 `timeout` 명령어를 빌려 쓸 수 있습니다.

```cpp
// 코드 복잡도를 획기적으로 줄여주는 방식
FILE* fp = popen("timeout 3s ./child_process", "r");
if (fp == NULL) {
    // 에러 처리
}
// 이후 fgets 등으로 결과 읽기...
pclose(fp);

```

**언제 무엇을 사용해야 할까요?**

* **`poll()` 방식:** 자식 프로세스와 실시간으로 데이터를 주고받으며, 수신 데이터 내용에 따라 타임아웃을 초기화하거나 로직을 변경해야 하는 **정교한 IPC**가 필요할 때.
* **`timeout` 도구:** 단순한 실행 억제가 목적이며, 코드 유지보수 비용을 최소화하고 싶을 때.

---

Date: 2026. 03. 13

Tags: fork, pipe, poll, timeout, ProcessManagement
