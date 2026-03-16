## 정밀한 타이머 구현하기: sleep_for vs sleep_until 완벽 정리

(gemini로 작성됨)

C++에서 일정 시간 대기하거나 주기적인 작업을 수행해야 할 때, 어떤 도구를 사용해야 할까요? 단순히 코드를 멈추는 것을 넘어, 오차 없는 정밀한 타이머를 만드는 방법을 정리해 봅니다.

### 1. C++ Standard Clock의 종류

타이머를 만들기 전, 기준이 되는 **Clock**을 올바르게 선택하는 것이 중요합니다. `<chrono>` 헤더에는 세 가지 주요 클록이 있습니다.

* **`std::chrono::system_clock`**: PC의 작업표시줄 시계와 같습니다. 사용자가 시간을 수정하면 같이 변하기 때문에, 로그 기록에는 좋지만 **타이머 로직에는 위험**합니다.
* **`std::chrono::steady_clock`**: 시스템 시각이 바뀌어도 영향을 받지 않고 일정한 속도로 흐르는 '스톱워치'입니다. **타이머와 성능 측정에 가장 적합**합니다.
* **`std::chrono::high_resolution_clock`**: 시스템에서 지원하는 가장 정밀한 단위의 시계입니다.

### 2. sleep_for vs sleep_until: 무엇이 다른가?

둘 다 실행을 일시 중지하지만, 목적지를 설정하는 방식이 다릅니다.

#### `sleep_for()` (상대적 대기)

* **방식**: "지금부터 1초 동안 쉬어라."
* **특징**: 호출된 시점을 기준으로 상대적인 시간을 대기합니다.
* **단점**: 루프 안에서 사용 시 **작업 소요 시간만큼 오차가 누적**됩니다.

#### `sleep_until()` (절대적 대기)

* **방식**: "다음 정각(10:00:01)이 될 때까지 쉬어라."
* **특징**: 특정 시점(time_point)을 지정하여 대기합니다.
* **장점**: 작업 시간이 길어져도 다음 실행 시점을 고정할 수 있어 **정밀한 주기 제어**가 가능합니다.

### 3. 실전 예제: steady_clock 기반의 정밀 타이머

`sleep_until`과 `steady_clock`을 조합하여 오차가 누적되지 않는 주기적 실행 루프를 구현한 예제입니다.

```cpp
#include <iostream>
#include <chrono>
#include <thread>

int main() {
    using namespace std::chrono;

    // 1. 기준 시점 설정
    auto next_wakeup = steady_clock::now();
    
    // 2. 주기 설정 (예: 1초)
    const auto interval = 1s;

    std::cout << "타이머를 시작합니다. (5회 반복)\n" << std::endl;

    for (int i = 0; i < 5; ++i) {
        // 다음 깨어날 목표 시각 계산
        next_wakeup += interval;

        // [작업 영역] -----------------------------------------
        std::cout << "[" << i + 1 << "회차] 작업 수행 중..." << std::endl;
        
        // 작업에 일정 시간(200ms)이 소요된다고 가정
        std::this_thread::sleep_for(200ms); 
        // ---------------------------------------------------

        // 목표 시각까지 남은 시간만큼만 정확히 대기
        // 작업에 0.2초를 썼다면, 여기선 0.8초만 대기하게 됨
        std::this_thread::sleep_until(next_wakeup);

        auto now = steady_clock::now();
        auto ms = duration_cast<milliseconds>(now.time_since_epoch()).count();
        std::cout << ">> 정각 실행 완료! (현재 Timestamp: " << ms % 10000 << "ms)\n\n";
    }

    std::cout << "타이머 종료." << std::endl;
    return 0;
}
```

### 요약

1. 시간 간격 측정이나 타이머에는 무조건 **`steady_clock`**을 쓰자.
2. 단순 지연은 **`sleep_for`**, 주기적인 정밀 작업은 **`sleep_until`**이 유리하다.
3. `sleep_until`을 사용하면 작업 소요 시간으로 인한 오차 누적을 방지할 수 있다.

---

Date: 2026. 03. 16

Tags: CPP, C++, timer, steady_clock, system_clock, sleep_for, sleep_until
