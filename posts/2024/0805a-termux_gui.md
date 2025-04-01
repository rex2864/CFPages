## termux gui

termux를 사용하는 이유는 [이전 post](https://blog.kylesoft.net/post?p=2024/0723a%2Dtermux_%EC%84%A4%EC%B9%98,_%EC%84%A4%EC%A0%95,_%EC%82%AC%EC%9A%A9)에서 언급했듯이 자체 개발 환경 구축이었다.
이전에는 editor로 emacs를 사용했었으나, termux만으로는 한글 입력이 원활하지 않아 불편함이 있어 emacs에서 vscode로 editor를 변경했었다.
termux 만으로는 vscode를 자체적으로 사용할 수 없었고, code-server를 termux에서 구동하고 web browser에서 접속해서 사용하는 형태였다.
web browser에서 동작하다보니 웹앱으로 설치해서 사용할 수 있기는 하지만 서버와의 재연결, reload, 단축키 사용 등에서 불편한 점이 있을 수 밖에 없었다.
그러다가 termux-x11을 통해서 GUI 환경을 구축할 수 있는 것을 알게되었고, 시도하게 되었다.

### termux:X11 설치/설정

[Termux:X11 github repo](https://github.com/termux/termux-x11)에서 apk 다운로드 후 설치

termux:X11 실행하여 Preferences 선택하여 설정 진입

Output 설정에서
- display resolution mode를 custom을 선택
- display resolution에서 해상도 설정 - ex: 1920x1200
- fullscreen 설정을 enable.

keyboard 설정에서
- show additional keyboard 설정을 disable (HW 키보드를 사용할 거라서...)
- Enable Accessibility service for intercepting system shortcuts automatically 설정을 enable<BR>
  (이것을 설정하기 위해서는 아래의 설정을 먼저 해줘야 한다)

안드로이드 설정 -> 애플리케이션 -> Termux:X11 -> 더보기 -> 제한된 권한 설정을 선택하여 활성화.

안드로이드 설정 -> 접근성 -> 설치된 앱 -> Termux:X11 KeyInterceptor 설정을 사용함(enable)으로.

adb를 통해서 "WRITE_SECURE_SETTIGS" permission을 활성화
- 안드로이드 설정 -> 태블릿/휴대전화 정보 -> 소프트웨어 정보 진입하여 빌드번호를 여러번 터치하여 개발자 옵션을 활성화
- 안드로이드 설정 -> 개발자 옵션으로 진입하여 USB 디버깅 옵션을 찾아서 enable
- PC와 USB cable을 연결하여 PC에서 adb shell로 진입하여 다음 명령을 실행<BR>
  `pm grant com.termux.x11 android.permission.WRITE_SECURE_SETTINGS`

### termux에 x11 환경 설치/설정

termux로 돌아와서...

```bash
pkg install x11-repo
pkg install termux-x11-nightly i3 st rofi
```

termux terminal에서 `termux-x11 :1 -xstartup "dbus-launch --exit-with-session i3"`으로 실행하고, termux:X11 app으로 전환 또는 실행하면 linux GUI 나옴!!!!

### i3wm 설정

기본 설정<BR>
~/.config/i3/config 파일에서 아래와 같이 불필요한 것들 주석 처리 또는 삭제

```bash
#exec --no-startup-id dex --autostart --environment i3
#exec --no-startup-id xss-lock --transfer-sleep-lock -- i3lock --nofork
#exec --no-startup-id nm-applet
```

터미널 실행 명령/단축키 설정을 i3-sensible-terminal에서 st로 변경<BR>
~/.config/i3/config 파일에서 기존 것을 주석처리하고 새로운 것을 추가

```bash
#bindsym $mod+Return exec i3-sensible-terminal
bindsym $mod+Return exec st
```

메뉴 실행 명령/단축키 설정을 dmenu에서 rofi로 변경<BR>
~/.config/i3/config 파일에서 기존 것을 주석처리하고 새로운 것을 추가

```bash
#bindsym $mod+d exec --no-startup-id dmenu_run
bindsym $mod+d exec --no-startup-id "rofi -modi drun,run -show drun"
```

### CapsLock키를 Ctrl로 사용하도록 설정해보자

`pkg install xorg-setxkbmap`으로 필요한 패키지 설치

~/.config/i3/config 파일에 아래 라인 추가

```bash
exec --no-startup-id setxkbmap -option ctrl:nocaps
```

i3를 재시작하면 적용됨

### 한글 입력이 되도록 해보자

필요한 패키지 설치

```bash
pkg install fcitx5 fcitx5-hangul fcitx5-configtool libuv fcitx5-gtk2 fcitx5-gtk3 fcitx5-gtk4
```

~/.config/i3/config 파일에 아래 내용 추가

```bash
exec --no-startup-id fcitx5
```

termux-x11 실행할때 다음과 같이 환경변수 추가 되도록

```bash
termux-x11 :1 -xstartup "GTK_IM_MODULE=fcitx QT_IM_MODULE=fcitx XMODIFIERS=@im=fcitx dbus-launch --exit-with-session i3"
```

`fcitx5-configtool`을 실행하여 `hangul`을 입력기 목록에 추가하고 Global Options에서 입력기간 전환 단축키 설정을 해준다. 나는 Shift+space로...

입력기 전환 단축키를 입력했을때 안드로이드 자체의 언어/입력기 전환이 된다면 Termux:X11 앱을 최소화 했다가 다시 열면 된다.

KeyInterceptor가 동작을 해야하는데 제대로 동작이 안될 때도 있는 것 같다.

### gtk application들에 dark theme 적용

~/.config/gtk-3.0 directory 생성하고, settings.ini 파일을 아래 내용으로 생성

```bash
[Settings]
gtk-application-prefer-dark-theme = true
```

### sound 관련 설치/설정

필요한 패키지 설치

```bash
pkg install pulseaudio pavucontrol
```

`$PREFIX/etc/bash.bashrc` 파일에 아래 내용 추가

```bash
LD_PRELOAD=/system/lib64/libskcodec.so pulseaudio --start --load="module-native-protocol-tcp auth-ip-acl=127.0.0.1 auth-anonymous=1" --exit-idle-time=-1
```

`LD_PRELOAD=/system/lib64/libskcodec.so` 부분은 oneUI 6.1을 위한 work around이다. oneUI 6.1을 사용하는 경우 이것이 없으면 sound card가 pulseaudio에 잡히지 않는다.

termux 재시작해서 적용되도록 한다.

### 각종 필요한 application 설치

firefox 설치: `pkg install firefox`

vscode opensource version: `pkg install code-oss`

---

Date: 2024. 08. 05

Tags: termux, termux-x11, i3, fcitx5, linux, 개발환경, gui, vscode, hangul
