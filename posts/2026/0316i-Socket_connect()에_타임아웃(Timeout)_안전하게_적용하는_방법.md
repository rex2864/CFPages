## Socket `connect()`에 타임아웃(Timeout) 안전하게 적용하는 방법

(gemini로 작성됨)

네트워크 프로그래밍을 하다 보면 외부 서버와 통신할 때 예기치 않은 지연을 마주하게 됩니다. 기본적으로 C/C++의 소켓 `connect()` 함수는 '블로킹(Blocking)' 방식으로 동작합니다. 즉, 서버가 응답하지 않거나 네트워크에 문제가 생기면, 연결이 성공하거나 OS의 기본 타임아웃(보통 수십 초에서 수 분)이 떨어질 때까지 스레드가 꼼짝없이 멈춰버리게 됩니다.

이러한 문제를 해결하고 애플리케이션의 반응성을 높이려면 **논블로킹(Non-blocking) 소켓**과 **I/O 멀티플렉싱(poll, select 등)**을 활용하여 직접 타임아웃을 구현해야 합니다.

이번 포스트에서는 `poll()`과 `CLOCK_MONOTONIC`을 활용하여 인터럽트(Interrupt)에도 안전한 `connect_with_timeout` 함수를 구현하는 방법을 알아보겠습니다.

### 핵심 구현 원리

타임아웃이 있는 연결을 구현하는 전체적인 흐름은 다음과 같습니다.

1. **소켓 상태 변경**: 소켓을 일시적으로 논블로킹(O_NONBLOCK) 모드로 변경합니다.
2. **연결 시도**: `connect()`를 호출합니다. 논블로킹 상태이므로 즉시 반환되며, 백그라운드에서 연결이 진행됩니다 (`EINPROGRESS`).
3. **타임아웃 대기**: `poll()` 함수를 사용하여 소켓에 쓰기 가능 이벤트(`POLLOUT`)가 발생할 때까지(즉, 연결이 완료될 때까지) 대기합니다.
4. **결과 검증**: 대기가 끝난 후 `getsockopt()`를 사용해 소켓에 실제로 에러가 발생했는지, 아니면 정상적으로 연결되었는지 확인합니다.
5. **상태 복구**: 소켓을 원래의 블로킹 상태로 되돌립니다.

### 전체 코드 구현 (`connect_with_timeout`)

아래는 위 로직을 반영하여 작성한 C/C++ 함수입니다.

> **주의:** 기존 코드에서 `fcntl` 결과값을 변수에 할당할 때 괄호 위치에 따른 연산자 우선순위 버그가 있어 안전하게 수정(`(sockfd_flags_before = fcntl(...)) < 0`)했습니다.

```cpp
#include <sys/socket.h>
#include <fcntl.h>
#include <poll.h>
#include <time.h>
#include <errno.h>

int connect_with_timeout(int sockfd, const struct sockaddr *addr, socklen_t addrlen, unsigned int timeout_ms) {
    int rc = 0;
    
    // 1. 현재 소켓 플래그를 가져오고 O_NONBLOCK 설정
    int sockfd_flags_before;
    if ((sockfd_flags_before = fcntl(sockfd, F_GETFL, 0)) < 0) return -1;
    if (fcntl(sockfd, F_SETFL, sockfd_flags_before | O_NONBLOCK) < 0) return -1;
    
    // 2. 비동기 연결 시작
    do {
        if (connect(sockfd, addr, addrlen) < 0) {
            // 즉시 실패한 경우 (진행 중인 상태가 아님)
            if ((errno != EWOULDBLOCK) && (errno != EINPROGRESS)) {
                rc = -1;
            } 
            // 연결이 백그라운드에서 진행 중인 경우 대기
            else {
                // 시스템 시간에 의존하지 않는 CLOCK_MONOTONIC으로 데드라인 설정
                struct timespec now;
                if (clock_gettime(CLOCK_MONOTONIC, &now) < 0) { rc = -1; break; }
                
                struct timespec deadline = { 
                    .tv_sec = now.tv_sec,
                    .tv_nsec = now.tv_nsec + timeout_ms * 1000000l 
                };
                
                // poll()이 EINTR(인터럽트)로 인해 깨어날 수 있으므로 루프 처리
                do {
                    if (clock_gettime(CLOCK_MONOTONIC, &now) < 0) { rc = -1; break; }
                    
                    // 남은 시간 계산
                    int ms_until_deadline = (int)( (deadline.tv_sec  - now.tv_sec) * 1000l
                                                 + (deadline.tv_nsec - now.tv_nsec) / 1000000l );
                    if (ms_until_deadline < 0) { rc = 0; break; } // 타임아웃
                    
                    // 연결 완료 또는 타임아웃까지 대기 (POLLOUT 이벤트)
                    struct pollfd pfds[] = { { .fd = sockfd, .events = POLLOUT } };
                    rc = poll(pfds, 1, ms_until_deadline);
                    
                    // poll이 성공적으로 반환되었을 때, 실제 연결 성공 여부 검증
                    if (rc > 0) {
                        int error = 0; 
                        socklen_t len = sizeof(error);
                        int retval = getsockopt(sockfd, SOL_SOCKET, SO_ERROR, &error, &len);
                        if (retval == 0) errno = error;
                        if (error != 0) rc = -1;
                    }
                } while (rc == -1 && errno == EINTR); // 인터럽트 발생 시 재시도
                
                // 타임아웃이 발생한 경우
                if (rc == 0) {
                    errno = ETIMEDOUT;
                    rc = -1;
                }
            }
        }
    } while (0);
    
    // 3. 소켓을 원래의 블로킹 상태로 복구
    if (fcntl(sockfd, F_SETFL, sockfd_flags_before) < 0) return -1;
    
    return rc;
}
```

### 코드 상세 분석: 왜 이렇게 짰을까?

* **`CLOCK_MONOTONIC`의 사용:** 시간을 측정할 때 시스템 시간(`CLOCK_REALTIME`)을 사용하면 중간에 관리자가 서버 시간을 강제로 변경하거나 NTP 동기화가 일어날 때 로직이 꼬일 수 있습니다. `CLOCK_MONOTONIC`은 부팅 이후 흘러간 절대적인 시간을 보장하므로 타임아웃 계산에 훨씬 안전합니다.
* **`EINTR` (인터럽트) 처리:** `poll()` 함수는 대기 도중 시스템 시그널을 받으면 `EINTR` 에러를 뱉으며 깨어납니다. 위 코드는 `while(rc==-1 && errno==EINTR)` 루프를 통해 인터럽트가 발생해도 남은 시간을 다시 계산하여 끈기 있게 기다리도록 견고하게 작성되었습니다.
* **`getsockopt`를 통한 이중 체크:** `poll`이 `POLLOUT`(쓰기 가능) 상태를 감지했다고 해서 무조건 연결에 성공한 것은 아닙니다. 서버가 연결을 거부(RST)한 경우에도 에러 정보를 쓸 수 있도록 소켓 상태가 변하기 때문입니다. 따라서 `SO_ERROR` 옵션을 사용해 진짜 성공인지 실패인지 확실히 판별해야 합니다.

---

Date: 2026. 03. 16

Tags: CPP, C언어, 네트워크프로그래밍, SocketProgramming, Timeout, poll, NonBlocking, 백엔드개발, 서버개발, Linux
