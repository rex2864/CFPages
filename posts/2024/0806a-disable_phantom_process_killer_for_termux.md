## disable phantom process killer for termux

termux github repository의 README를 확인해보면 아래와 같은 NOTICE가 있는 것을 볼 수 있다.

> NOTICE: Termux may be unstable on Android 12+. Android OS will kill any (phantom) processes greater than 32 (limit is for all apps combined) and also kill any processes using excessive CPU. You may get `[Process completed (signal 9) - press Enter]` message in the terminal without actually exiting the shell process yourself. Check the related issue [#2366](https://github.com/termux/termux-app/issues/2366), [issue tracker](https://issuetracker.google.com/u/1/issues/205156966), [phantom cached and empty processes docs](https://github.com/agnostic-apollo/Android-Docs/blob/master/en/docs/apps/processes/phantom-cached-and-empty-processes.md) and [this TLDR comment](https://github.com/termux/termux-app/issues/2366#issuecomment-1237468220) on how to disable trimming of phantom and excessive cpu usage processes. A proper docs page will be added later. An option to disable the killing should be available in Android 12L or 13, so upgrade at your own risk if you are on Android 11, specially if you are not rooted.

Notice 내에 언급된 link들을 참고하여 진행하면 되지만...

내용이 정리되어 있지 않아서 따로 정리해 본다.

이미 정리해둔 다른 document들을 참고하였다. [link](https://maheshtechnicals.com/fix-termux-error-process-completed-signal-9-disable-phantom-process-killer-in-android-12-13/)

### 필요한 이유

termux를 사용하다보면 NOTICE에 언급된 것처럼 `[Process completed (signal 9) - press Enter]`를 출력하면서 termux가 죽을때가 있다.

다시 실행하면 되기는 하지만, 작업 중이었던 것들이 날라가기도 하고, 흐름이 깨지기도 한다.

죽지 않게 해보자.

### 안드로이드 version 12 & 13에서 ADB를 사용

ADB shell로 진입해서 다음 command들을 실행한다.

```
/system/bin/device_config set_sync_disabled_for_tests persistent
/system/bin/device_config put activity_manager max_phantom_processes 2147483647
settings put global settings_enable_monitor_phantom_procs false
```

제대로 설정되었는지 확인하려면 아래 명령들을 사용한다.

```
/system/bin/dumpsys activity settings | grep max_phantom_processes
/system/bin/device_config get activity_manager max_phantom_processes
```

### 안드로이드 version 14 이상에서 개발자 옵션을 통해서 설정 가능

설정 -> 개발자 옵션 -> 자식 프로세 제한 중지 옵션을 활성화

이 경우 개발자 옵션을 활성화 상태로 유지해야한다. disable하면 설정이 풀린다.

---

Date: 2024. 08. 06

Tags: phantom, termux, linux, 개발환경, phantom_process, android, 안드로이드
