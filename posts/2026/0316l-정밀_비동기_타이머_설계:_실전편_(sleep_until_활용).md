## 정밀 비동기 타이머 설계: 실전 편 (sleep_until 활용)

(gemini로 작성됨)

C++에서 단순한 딜레이를 넘어, 메인 로직을 방해하지 않으면서 정밀하게 작동하는 **비동기 타이머 클래스**를 설계하는 방법을 알아보겠습니다.

### 1. Clock 선택의 기술: 왜 steady_clock인가?

타이머의 생명은 **일관성**입니다.

* **`system_clock`**: 네트워크 동기화나 사용자 설정에 의해 시각이 바뀔 수 있습니다. (10초 타이머가 갑자기 1시간이 될 수 있음)
* **`steady_clock`**: 하드웨어 클록을 기준으로 일정하게 증가합니다. **타이머 로직에는 반드시 이 클록을 사용해야 합니다.**

### 2. 정밀도 해결: sleep_for vs sleep_until

반복 루프에서 `sleep_for(1s)`를 쓰면 `작업 시간 + 1초`가 소요되어 시간이 지날수록 오차가 누적됩니다. 반면 `sleep_until`은 다음 실행 시점을 미리 점찍어두고 대기하므로 오차를 상쇄합니다.

### 3. 실전: 비동기 타이머 클래스 설계 (C++11/14)

별도의 스레드에서 주기적인 작업을 수행하며, 필요할 때 언제든 멈출 수 있는 클래스 구조입니다.

```cpp
#include <iostream>
#include <chrono>
#include <thread>
#include <atomic>
#include <functional>

class AsyncTimer {
public:
    AsyncTimer() : active(false) {}
    ~AsyncTimer() { stop(); }

    // 주기적 작업 시작 (함수 객체, 간격)
    void start(std::function<void()> task, std::chrono::milliseconds interval) {
        if (active.load()) return; // 이미 실행 중이면 무시

        active.store(true);
        worker_thread = std::thread([this, task, interval]() {
            auto next_wakeup = std::chrono::steady_clock::now();

            while (active.load()) {
                next_wakeup += interval; // 다음 실행 시점 계산
                
                task(); // 작업 수행

                // 목표 시점까지 남은 시간만큼 정밀하게 대기
                std::this_thread::sleep_until(next_wakeup);
            }
        });
    }

    void stop() {
        if (active.load()) {
            active.store(false);
            if (worker_thread.joinable()) {
                worker_thread.join();
            }
        }
    }

private:
    std::atomic<bool> active;      // 스레드 안전한 상태 제어
    std::thread worker_thread;     // 배경에서 돌아갈 스레드
};

int main() {
    AsyncTimer timer;

    std::cout << "메인 로직 시작..." << std::endl;

    // 1초마다 현재 시간을 출력하는 비동기 작업 시작
    timer.start([]() {
        std::cout << "[Timer] 틱(Tick) 발생!" << std::endl;
    }, std::chrono::milliseconds(1000));

    // 메인 스레드는 타이머와 상관없이 자기 할 일을 함
    std::this_thread::sleep_for(std::chrono::seconds(5));

    std::cout << "메인 로직 종료 및 타이머 정지." << std::endl;
    timer.stop();

    return 0;
}
```

### 4. 설계 포인트 요약

#### 1) std::atomic 사용

메인 스레드에서 `stop()`을 호출하고, 워커 스레드에서 루프 조건을 확인할 때 **데이터 레이스(Data Race)**가 발생하지 않도록 `std::atomic<bool>`을 사용하여 스레드 안전성을 확보했습니다.

#### 2) RAII 패턴 적용

소멸자(`~AsyncTimer`)에서 `stop()`을 호출하여, 객체가 사라질 때 스레드가 안전하게 종료(join)되도록 설계했습니다. 이는 좀비 스레드 생성을 방지하는 중요한 습관입니다.

#### 3) 오차 누적 방지 (Drift Compensation)

`next_wakeup += interval` 방식을 통해, `task()` 실행에 시간이 얼마나 걸리든 전체적인 주기는 일정하게 유지됩니다.

### 마치며

단순히 코드를 멈추는 것과 '정밀한 타이밍'을 맞추는 것은 큰 차이가 있습니다. C++의 `<chrono>`와 `<thread>`를 적절히 조합하면 외부 라이브러리 없이도 훌륭한 타이머를 구축할 수 있습니다.

더 높은 수준의 비동기 제어가 필요하다면 **Boost.Asio**의 `steady_timer`를 살펴보는 것도 추천합니다.

---

Date: 2026. 03. 16

Tags: CPP, C++, timer, steady_clock, system_clock, sleep_for, sleep_until, async
