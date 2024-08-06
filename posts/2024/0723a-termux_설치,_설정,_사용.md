## termux 설치, 설정, 사용

개인적으로 home server를 구축해 놓고 필요할때는 원격으로 terminal 접속을 하여 활용/사용하고는 했었다.

외부에서 접근에 대해서는 SSH만 허용하고 사용하다가 보안적인 면에서 위험성이 다분하여 여러 방법을 찾아보고 활용하고 있었다.
cloudflare tunnel을 사용하고, 그 위에 wetty를 설치/설정, cloudflare tunnel에 대해서 인증 적용한 방법을 한동안 사용하다가,
VPN server를 구축해놓고, VPN을 통해서 server에 접속하는 방법도 사용했었다.

그러다가, 원격으로 SSH 연결하는 것 자체를 없앨 수 있는 방법이 없을까 고민하기 시작했다.
데이터 요금도 걱정되기도 하고, 잠시 다른 일을 하거나 자리를 비우거나 할때 항상 접속을 끊었다가 다시 접속해야하는 불편함 때문이었다.
이것저것 찾아서 시도를 하던중에 termux를 찾을 수 있었고, 딱 원하던 것이라 설치하여 지금까지 잘 사용/활용하고 있다.

termux는 안드로이드 안에서 별개로 linux를 사용할 수 있게 해준다.
원격으로 동작하는 것이 아니라 local에서 동작하므로 별도 서버에 연결을 할 필요가 없으며 데이터 요금 걱정도 할 필요가 없다.
완전한 별도의 linux machine처럼 사용할 수 있으므로 linux service/application들을 동일하게 사용할 수 있다.

### 설치

termux는 F-Droid에서 설치하는 것을 권장한다.

termux document의 installation을 확인하여 설치하도록 하자

[termux installation](https://wiki.termux.com/wiki/Installing_from_F-Droid)

설치가 되면 icon을 선택하여 실행하면 termux terminal을 만날 수 있다.
일반적인 linux terminal 환경과 동일하므로 linux terminal 사용하듯이 사용하면 된다.

### 설정

다른 것을 하기 전에 우선 업데이트를 하도록 하자.

```
pkg update
pkg upgrade
```

외부 키보드를 사용하는 경우 화면 하단에 표시되는 특수 키들을 사용할 일이 없으므로 보이지 않도록 설정하면 화면을 더 크게 사용할 수 있다.
`nano ~/.termux/termux.properties` 명령으로 termux 설정 파일을 열고 아래 항목을 추가하도록 하자.
```
extra-keys = []
```

termux terminal내에서 한글을 입력할 경우 바로 입력이 되지 않고 space나 enter를 입력해야만 비로소 입력했던 한글이 적용되는 것을 확인할 수 있다.
역시 termux 설정파일을 열어서 `nano ~/.termux/termux.properties` 아래 항목을 설정하도록 하자.
```
enforce-char-based-input = true
```

### 프로그램 설치

home server나 termux를 사용하려던 목적이 개인적인 프로젝트 진행이었다.
C/C++을 사용하여 프로그램을 작성하거나, webserver를 통해서 web service를 개발하는 등의 목적이었다.
관련 프로그램을 설치하여 사용하도록 하자.

기본 repository에 없는 프로그램을 사용하기 위해서 아래와 같이 tur-repo를 추가 설치하도록 하자.
```
pkg install tur-repo
```

editor로 주로 사용하고 있는 emacs를 설치
```
pkg install emacs
```

web service를 위한 webserver로 lighttpd를 설치
```
pkg install lighttpd
```

개발 언어(C/C++, python) 및 개발 관련 tool 설치
```
pkg install clang python make cmake git
```

### termux extension, addon

#### termux-services

linux에서 systemd를 통해 service들을 관리하듯이 termux에서 service들을 관리할 수 있다.
systemd와는 사용법이 다르다.

자세한 것은 termux-services document를 확인하자.

[termux-services](https://wiki.termux.com/wiki/Termux-services)

#### termux:boot

안드로이드를 완전히 껐다가 켜거나, 재부팅을 하거나 했을때 설정된 termux properties를 적용하거나
원하는 프로그램을 바로 실행하도록 도와주는 addon이다.
termux-services를 실행하도록 설정하고, termux-services에서 원하는 service를 실행/관리하도록 하면 좋다.

상세한 것은 termux:boot document를 확인하자.

[termux-boot](https://wiki.termux.com/wiki/Termux:Boot)

---

Date: 2024. 07. 23

Tags: termux, F-Droid, home_server, linux, 개발환경, terminal
