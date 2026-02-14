## windows capslock to ctrl

(gemini로 작성함)


Windows에서 Caps Lock 키를 Control 키로 변경하는 방법은 레지스트리를 직접 수정하는 것이 가장 깔끔한 방법입니다.
이 방식은 별도의 상주 프로그램을 설치하지 않아도 된다는 장점이 있습니다.


### 1. 레지스트리 편집기(.reg) 파일 만들기

메모장을 열고 아래 내용을 복사하여 붙여넣으세요.

```registry
Windows Registry Editor Version 5.00

[HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Keyboard Layout]
"Scancode Map"=hex:00,00,00,00,00,00,00,00,02,00,00,00,1d,00,3a,00,00,00,00,00
```

* **파일 저장:** `caps_to_ctrl.reg`와 같이 확장자를 **.reg**로 설정하여 저장합니다.
* **실행:** 저장한 파일을 더블 클릭하여 레지스트리에 병합합니다.
* **적용:** 컴퓨터를 **재부팅**하거나 로그아웃 후 다시 로그인하면 설정이 적용됩니다.


### 2. 레지스트리 값의 의미 (기술적 배경)

이 설정은 `Scancode Map`이라는 이진 값을 통해 키보드의 신호를 가로채는 방식입니다.

| 데이터 구간               | 의미                                                     |
|---------------------------|----------------------------------------------------------|
| `00,00,00,00,00,00,00,00` | 헤더 및 버전 정보 (고정값)                               |
| `02,00,00,00`             | 변경할 항목의 개수 (1개 변경 + 종료 플래그 1개 = 총 2개) |
| `1d,00,3a,00`             | **핵심:** Caps Lock(`3a`)을 Left Control(`1d`)로 매핑    |
| `00,00,00,00`             | 설정 종료 알림                                           |


### 3. 원상태로 복구하는 방법

만약 다시 원래대로 되돌리고 싶다면, 아래 내용을 메모장에 복사해 실행하거나 레지스트리 편집기(`regedit`)에서
해당 경로의 `Scancode Map` 값을 삭제하면 됩니다.

```registry
Windows Registry Editor Version 5.00

[HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Keyboard Layout]
"Scancode Map"=-
```

---

Date: 2026. 02. 15

Tags: windows, capslock, ctrl
