## 멀티스레딩 디버깅의 필수: std::thread 이름 설정하기 (pthread 활용)

(gemini로 작성됨)

복잡한 멀티스레드 애플리케이션을 개발하다 보면 `gdb`로 디버깅을 하거나 `top`, `htop` 등의 시스템 모니터링 도구로 프로세스를 분석해야 할 때가 많습니다. 이때 모든 스레드 이름이 메인 프로세스와 동일하게 표기된다면, 어떤 스레드가 데드락(Deadlock)에 빠졌는지, 어떤 스레드가 CPU 리소스를 독점하고 있는지 파악하기가 매우 어렵습니다.

아쉽게도 C++의 `std::thread`는 기본적으로 스레드 이름을 설정하는 표준 API를 제공하지 않습니다. 하지만 리눅스나 POSIX 호환 시스템에서는 `pthread` 라이브러리의 확장 함수를 사용하여 이 문제를 간단히 해결할 수 있습니다.

이번 포스트에서는 `pthread_setname_np`를 활용하여 C++ 스레드에 이름을 부여하는 두 가지 방법을 알아보겠습니다.

### 1. 현재 실행 중인 스레드 이름 스스로 설정하기

스레드가 실행하는 작업 함수 내부에서 자기 자신의 이름을 직접 설정하는 방법입니다. `pthread_self()`를 호출하여 현재 스레드의 핸들을 가져와서 이름을 부여합니다.

```cpp
#include <thread>
#include <iostream>
#include <pthread.h>
#include <string>

using namespace std;

void foo()
{
    string thread_name = "WorkerThread-1";
    char name_buffer[16];

    // 1. 현재 스레드의 이름 설정
    // pthread_self()는 현재 실행 중인 스레드의 pthread_t 핸들을 반환합니다.
    pthread_setname_np(pthread_self(), thread_name.c_str());

    // 2. 설정된 스레드 이름 읽어오기
    pthread_getname_np(pthread_self(), name_buffer, sizeof(name_buffer));  
    
    cout << "Current Thread Name: " << name_buffer << endl;
}

int main()
{
    // 스레드 생성 및 실행
    thread t1(foo);

    t1.join();
    return 0;
}
```

### 2. 외부에서 특정 스레드 객체의 이름 설정하기 (Wrapper 함수)

스레드를 생성하고 관리하는 매니저 클래스나 메인 스레드에서 생성된 자식 스레드의 이름을 외부에서 지정해주고 싶을 때가 있습니다. 이때는 `std::thread` 객체의 `native_handle()` 메서드를 사용하여 내부의 `pthread_t` 핸들을 추출할 수 있습니다.

아래와 같이 유틸리티 함수를 하나 만들어두면 매우 편리하게 재사용할 수 있습니다.

```cpp
#include <thread>
#include <string>
#include <pthread.h>

namespace os {
    // std::thread 객체와 부여할 이름을 받아 스레드 이름을 설정하는 래퍼(Wrapper) 함수
    void setThreadName(std::thread &thread, const std::string &name)
    {
        // std::thread에서 POSIX 스레드 핸들을 추출
        pthread_t handle = thread.native_handle();
        
        // 해당 핸들에 이름 부여
        pthread_setname_np(handle, name.c_str());
    }
}
```

### 주의사항 및 팁

* **16바이트 길이 제한**: 리눅스에서 스레드 이름은 널 종료 문자(`\0`)를 포함하여 **최대 16바이트**까지만 지정할 수 있습니다. 즉, 실제 영문자 기준 15자까지만 입력 가능하며, 이를 초과하면 `pthread_setname_np` 함수가 에러(ERANGE)를 반환하고 이름이 설정되지 않습니다.
* **`_np`의 의미**: 함수 이름 끝에 붙은 `_np`는 **N**on-**P**ortable의 약자입니다. 즉, POSIX 표준에 속하지 않는 플랫폼 종속적인 확장이므로, 윈도우(Windows)나 다른 OS 환경에서는 컴파일되지 않을 수 있습니다.
* **모니터링 방법**: 스레드 이름을 설정한 후 리눅스 터미널에서 `top -H -p <프로세스ID>` 명령을 실행해 보세요. 지정한 스레드 이름이 목록에 예쁘게 출력되는 것을 확인할 수 있습니다.

---

Date: 2026. 03. 16

Tags: CPP, C++, Multithreading, 멀티스레딩, 디버깅, pthread, Linux, 리눅스개발, 서버개발, 성능최적화
