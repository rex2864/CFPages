## docker install to alpine linux

(gemini로 작성함)


### 1. 리포지토리 활성화 및 시스템 업데이트

Docker 패키지가 포함된 community 리포지토리 활성화

/etc/apk/repositories 파일을 확인하여 community 라인의 주석(#)을 제거한 뒤 아래 명령어를 실행

```bash
doas apk update
```


### 2. Docker 패키지 설치

Docker 엔진과 함께 최신 버전의 Compose 플러그인을 설치

```bash
doas apk add docker docker-cli-compose
```


### 3. 부팅 시 자동 실행 설정

시스템이 시작될 때마다 Docker 데몬이 자동으로 실행되도록 설정

alpine은 OpenRC를 사용하므로 rc-update를 활용

```bash
doas rc-update add docker boot
```


### 4. Docker 서비스 시작

설치 직후에는 서비스가 중지된 상태. 아래 명령어로 즉시 실행

```bash
doas service docker start
```


### 5. 사용자 권한 설정 (일반 사용자용)

매번 sudo나 doas를 붙이지 않고 Docker 명령어를 사용하려면, 현재 사용자를 docker 그룹에 추가해야 함

```bash
doas usermod -aG docker $USER
```


### 6. 시스템 재부팅

그룹 변경 사항을 시스템에 완전히 적용하기 위해 재부팅이 필요

```bash
reboot
```


### 7. 설치 확인 (Hello-World 실행)

모든 설정이 정상적으로 완료되었는지 확인하기 위해 테스트 이미지를 실행해 보자

```bash
docker run hello-world
```

---

Date: 2026. 02. 14

Tags: docker, alpine
