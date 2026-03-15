## 히스토리 없이 가볍고 빠르게 Clone & Sync 하는 방법 (Shallow Clone)

(gemini로 작성됨)

규모가 큰 프로젝트(AOSP, 리눅스 커널 등)의 소스 코드를 내려받을 때,
수년 치의 커밋(Commit) 히스토리와 태그(Tag)를 모두 가져오면 엄청난
시간과 디스크 용량이 소모됩니다.

단순히 최신 소스 코드를 빌드하거나 분석하는 것이 목적이라면,
과거의 불필요한 이력 없이 **최신 상태만 가볍게 가져오는
'Shallow Clone'** 방식을 사용하는 것이 훨씬 효율적입니다.
이번 글에서는 `git`과 `repo` 환경에서 히스토리 없이 가볍게
소스를 동기화하는 방법을 정리해 보겠습니다.

### 1. Git에서 가볍게 Clone 하기

단일 Git 저장소를 복제할 때는 `--depth`와 `--no-tags` 옵션을 활용합니다.

```bash
git clone --depth 1 --no-tags <저장소_URL>
```

* **`--depth 1`**: 전체 커밋 히스토리를 무시하고, 가장 최근의 최신 커밋 1개만 가져옵니다.
* **`--no-tags`**: 불필요한 태그(Tag) 정보들을 내려받지 않아 용량과 시간을 추가로 절약합니다.

### 2. Repo(Google Repo Tool)에서 가볍게 Init & Sync 하기

여러 개의 Git 저장소를 관리하는 `repo` 툴을 사용할 때는
`init`과 `sync` 단계에서 각각 적절한 옵션을 주어야 합니다.
**옵션의 위치와 순서**에 주의해서 작성하는 것이 좋습니다.

#### 2-1. Repo Init 설정

`repo init`을 수행할 때는 manifest 파일 설정과 로컬 레퍼런스(Reference) 설정 뒤에 각각 관련 옵션을 배치하면 깔끔합니다.

```bash
repo init -u <URL> -m sample.xml -c --no-tags --reference=sample_path --depth=1
```

* **`-c --no-tags`**: Manifest 파일과 관련된 설정이므로 `-m sample.xml` 뒤에 위치시킵니다. 현재 브랜치의 내용(`-c`, current-branch)만 가져오고, 태그는 제외(`--no-tags`)합니다.
* **`--depth=1`**: 로컬 캐시를 참조하는 `--reference=sample_path` 옵션 바로 뒤에 사용하여, 얕은 복제(최신 커밋 1개)를 수행하도록 지시합니다.

#### 2-2. Repo Sync 설정

초기화(Init)가 완료된 후, 실제로 소스 코드를 다운로드(동기화)하는 `sync` 명령어에도 옵션을 추가해 줍니다.

```bash
repo sync -c --no-tags
```

* `init` 때와 마찬가지로 현재 브랜치(`-c`)만 가져오고, 태그(`--no-tags`)를 무시하여 동기화 속도를 극대화합니다.

> **💡 요약하자면!**
> 과거 이력이 필요 없는 빌드 전용 서버나, 빠르게 소스만 확인하고 싶을 때는 항상 `--depth 1`과 `--no-tags` (Repo의 경우 `-c` 포함) 조합을 기억해 두시면 쾌적한 작업 환경을 만들 수 있습니다.

---

Date: 2026. 03. 15

Tags: Git, Repo, ShallowClone, 버전관리, 개발팁, 최적화, AOSP, 빌드서버
