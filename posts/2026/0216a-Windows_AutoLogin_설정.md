## Windows AutoLogin 설정

(gemini로 작성됨)


PC를 켤 때마다 매번 비밀번호나 PIN을 입력하지 않고 자동으로 로그인되도록 설정해보자.

쉬운 공식 툴 사용법부터, 레지스트리 수동 편집까지 단계별로 알아보자.


### 1. [가장 추천] Microsoft 공식 'Autologon' 툴 사용하기

가장 빠르고, 안전하며 확실한 방법입니다. 마이크로소프트에서 공식 제공하는 기술 도구인
Sysinternals Autologon을 사용하면 복잡한 설정 없이 클릭 몇 번으로 끝납니다.

* 다운로드: [Microsoft 공식 홈페이지 다운로드](https://learn.microsoft.com/en-us/sysinternals/downloads/autologon)
* 사용 방법:
  1. 다운로드한 압축 파일을 풀고 `Autologon.exe`를 실행합니다.
  2. 사용자 이름(Username), 도메인(기본값 유지), 비밀번호(Password)를 입력합니다.
  3. 'Enable' 버튼을 클릭하면 즉시 설정이 완료됩니다.

* 특징: 레지스트리를 직접 건드리지 않아도 툴이 알아서 안전하게 처리해주며, 해제하고 싶을 땐 실행 후 'Disable'만 누르면 됩니다.


### 2. 기본 기능을 이용한 설정 (netplwiz)

별도의 프로그램을 다운로드하고 싶지 않을 때 사용하는 윈도우 기본 방식입니다.

1. `Win + R` 키를 누르고 `netplwiz`를 입력한 뒤 엔터를 누릅니다.
2. 사용자 계정 창에서 '사용자 이름과 암호를 입력해야 이 컴퓨터를 사용할 수 있음' 항목의 체크를 해제합니다.
3. '확인'을 누른 뒤, 자동 로그인할 계정의 실제 비밀번호를 입력합니다. (PIN 번호가 아님에 주의하세요!)
4. 재부팅 후 설정이 적용되었는지 확인합니다.


### 💡 잠깐! '사용자 이름과 암호...' 체크 박스가 안 보인다면?

최신 Windows 10/11에서는 보안 정책 때문에 이 체크 박스가 숨겨져 있는 경우가 많습니다.
이럴 때는 아래의 레지스트리 설정(Step A)을 통해 메뉴를 다시 활성화해야 합니다.


### 3. [고급] 레지스트리 편집기(regedit) 완전 수동 설정

메뉴가 숨겨져 있거나 UI 방식이 작동하지 않을 때 사용하는 가장 강력한 수동 방법입니다.

#### Step A: 숨겨진 체크 박스 활성화하기

1. `Win + R` 누르고 `regedit`을 입력합니다.
2. 아래 경로로 이동합니다.
  > `HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\PasswordLess\Device`
3. `DevicePasswordLessBuildVersion` 값을 더블 클릭하여 `0`으로 수정합니다.
4. 이제 다시 `netplwiz`를 실행하면 숨겨졌던 체크 박스가 나타납니다.

#### Step B: 로그인 정보 레지스트리에 직접 등록하기

UI를 거치지 않고 직접 로그인 정보를 입력하는 방식입니다.

1. 아래 경로로 이동합니다.
  > `HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon`
2. 다음 항목들을 각각 찾아 값을 수정(없다면 우클릭 - 새로 만들기 - 문자열 값)합니다.
  * `AutoAdminLogon`: 값을 `1`로 수정
  * `DefaultUserName`: 로그인할 계정 이름 입력
  * `DefaultPassword`: 해당 계정의 비밀번호 입력


### ⚠️ 주의사항: 보안을 잊지 마세요!

자동 로그인은 편리하지만, 누군가 내 PC를 켜는 즉시 모든 데이터에 접근할 수 있게 됩니다.

* 권장: 집에서 사용하는 데스크톱, 물리적으로 안전한 장소의 PC
* 비권장: 휴대용 노트북, 외부 카페 이용 기기, 공용 PC

편의성만큼 중요한 보안! 상황에 맞춰 신중하게 설정해 보세요.

---

Date: 2026. 02. 16

Tags: windows, autologin
