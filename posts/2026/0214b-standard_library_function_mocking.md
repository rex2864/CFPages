## standard library function mocking

### LD_PRELOAD와 dlsym을 이용한 함수 모킹(Mocking) 기법

개발을 하다 보면 시스템 함수(예: `fopen`, `printf`, `malloc`)의 동작을 소스 코드 수정 없이
바꾸고 싶을 때가 있다. 특히 테스트 환경에서 난수 값을 고정하거나, 특정 파일 접근을 가로채야
하는 경우 **라이브러리 인터포지션(Library Interposition)** 기법이 매우 유용하다.

### 1. 라이브러리 인터포지션이란?

프로그램이 실행될 때 표준 라이브러리(libc)의 함수 대신,
**사용자가 정의한 함수를 우선적으로 연결**하게 만드는 기법.
이를 통해 마치 "가짜 함수(Mock)"를 중간에 끼워 넣는 것과 같은 효과를 낸다.

### 2. 핵심 코드 분석

아래는 `/dev/urandom`으로부터 읽어오는 난수 값을 특정 값(`0xdeadbeef`)으로 고정하는 예제 코드.

```c
#define _GNU_SOURCE
#include <stdio.h>
#include <dlfcn.h>
#include <string.h>

static int mock_file_contents = 0xdeadbeef;

// 1. 가짜 fopen 구현
static FILE *mock_fopen(const char *path, const char *mode) {
    return strcmp(path, "/dev/urandom") == 0
        ? fmemopen(&mock_file_contents, sizeof mock_file_contents, mode)
        : NULL;
}

static int use_mock_fopen = 0;

// 2. 표준 fopen 가로채기
FILE *fopen(const char *path, const char *mode) {
    FILE *(*real_fopen)(const char *, const char *);

    // RTLD_NEXT를 사용하여 실제 표준 라이브러리의 fopen 주소를 찾음
    *(void **) (&real_fopen) = dlsym(RTLD_NEXT, "fopen");

    // 플래그에 따라 가짜 또는 진짜 함수 호출
    return use_mock_fopen ? mock_fopen(path, mode) : real_fopen(path, mode);
}
```

#### 왜 컴파일 에러가 나지 않을까?

`stdio.h`에 이미 `fopen`이 선언되어 있음에도 에러가 나지 않는 이유는
**C의 링킹 구조** 때문. 링커는 실행 파일 내부에 정의된 심볼을 공유
라이브러리(`libc.so`)보다 먼저 탐색하므로, 새로 정의한 `fopen`이 우선권을 갖게 됨.

### 3. 가변 인자 함수(printf) 모킹하기

`printf`와 같은 가변 인자 함수도 모킹이 가능하다. 다만, 인자 전달을 위해
`va_list`와 `v` 계열 함수를 사용해야 한다.

```c
#include <stdarg.h>

int printf(const char *format, ...) {
    static int (*real_printf)(const char *, ...) = NULL;
    if (!real_printf) real_printf = dlsym(RTLD_NEXT, "printf");

    va_list args;
    va_start(args, format);
    
    printf("[MOCKED] "); // 커스텀 동작
    int result = vfprintf(stdout, format, args); // v계열 함수로 인자 전달
    
    va_end(args);
    return result;
}
```

*주의: 내부에서 다시 `printf`를 호출하면 무한 루프에 빠질 수 있으므로, 저수준 함수나 `real_printf`를 직접 호출해야 한다.*

### 4. 실전 디버깅 활용 사례

이 기법은 `LD_PRELOAD` 환경 변수와 결합했을 때 진정한 위력을 발휘한다.

1. **시간 조작**: `gettimeofday`를 가로채 프로그램에 가짜 시간을 주입 (예: 라이선스 만료 테스트)
2. **메모리 추적**: `malloc`/`free`를 가로채서 메모리 누수 지점 탐지
3. **네트워크/파일 격리**: 특정 파일 경로를 읽으려 할 때 다른 경로로 리다이렉트하여 샌드박싱 구현

### 5. 컴파일 및 실행 방법

동적 라이브러리 기능을 사용하므로 `-ldl` 옵션이 필수.

```bash
# 1. 공유 라이브러리로 빌드
gcc -fPIC -shared -o libmock.so mock.c -ldl

# 2. LD_PRELOAD를 사용하여 실행 (소스 수정 없이 가로채기 가능)
LD_PRELOAD=./libmock.so ./my_program
```

---

Date: 2026. 02. 14

Tags: C, programming, mocking
