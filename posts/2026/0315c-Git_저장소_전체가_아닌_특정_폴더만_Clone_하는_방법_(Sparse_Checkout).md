## Git 저장소 전체가 아닌 특정 폴더만 Clone 하는 방법 (Sparse Checkout)

(gemini로 작성됨)

Git 저장소의 크기가 매우 크거나 하나의 저장소에 여러 프로젝트가 묶여 있는 경우(모노레포 등), 전체 저장소를 `clone` 하는 것은 시간과 용량 면에서 비효율적일 수 있습니다.

이럴 때는 Git의 **Sparse Checkout** 기능을 활용하여 원하는 특정 디렉토리(폴더)만 선택적으로 다운로드할 수 있습니다.

### 방법 1: 최신 버전 Git (2.25 이상)에서의 초간단 방법 (추천!)

Git 2.25 버전부터는 복잡하게 설정 파일을 직접 수정할 필요 없이, 전용 명령어인 `git sparse-checkout`을 지원합니다. 본인의 Git 버전(`git --version`으로 확인)이 2.25 이상이라면 이 방법을 강력히 추천합니다.

**1. Sparse 모드로 뼈대만 클론하기**

처음부터 `--sparse` 옵션을 주고 클론합니다. 이 명령어는 최상위 디렉토리의 기본 파일들만 가져오고 하위 폴더는 비워둡니다.

(`--filter=blob:none` 옵션을 함께 쓰면 당장 필요 없는 파일의 히스토리 내역은 가져오지 않아 속도가 훨씬 빨라집니다.)

```bash
git clone --filter=blob:none --sparse <저장소 주소>
cd <생성된_저장소_폴더명>
```

**2. 원하는 특정 폴더 지정하여 가져오기**

이제 `set` 명령어로 다운로드하고 싶은 특정 폴더 경로만 지정해 주면 해당 폴더의 파일들이 즉시 다운로드됩니다.

```bash
git sparse-checkout set <가져올/폴더/경로>
```

*(예시: `git sparse-checkout set typescript-typeorm/src`)*

### 방법 2: 구버전 Git에서의 수동 설정 방법 (전통적인 방식)

만약 구버전 Git을 사용해야 하는 환경이거나, 기존 방식대로 직접 세팅하고 싶다면 아래 5단계를 차근차근 따라 해보세요.

**1. 로컬 저장소 초기화**

코드를 다운로드받을 빈 폴더를 하나 생성하고, 터미널에서 해당 폴더로 이동한 뒤 Git을 초기화합니다.

```bash
git init
```

**2. 원격 저장소 연결**

코드를 가져올 타겟 원격 저장소(Remote Repository)의 주소를 연결해 줍니다.

```bash
git remote add origin <저장소 주소>
```

**3. Sparse Checkout 활성화**

Git 설정에서 Sparse Checkout 기능을 사용하겠다고 명시적으로 활성화합니다.

```bash
git config core.sparsecheckout true
```

**4. 가져올 폴더 경로 설정**

어떤 폴더를 가져올지 `.git/info/sparse-checkout` 파일에 경로를 적어줍니다.

```bash
echo 폴더경로/* >> .git/info/sparse-checkout
```

> **주의 사항**
> 경로를 작성할 때 **큰따옴표("")나 작은따옴표('')를 사용하면 정상적으로 작동하지 않습니다.** 따옴표 없이 경로만 입력해 주세요. (예: `echo typescript-typeorm/src/* >> .git/info/sparse-checkout`)

**5. 소스 코드 가져오기 (Pull)**

경로 설정이 끝났다면, 마지막으로 `pull` 명령어를 사용해 해당 폴더의 데이터를 가져옵니다.

```bash
git pull origin master
```

*(원격 저장소의 기본 브랜치 이름이 `main`이라면 `git pull origin main`을 입력해 주세요.)*

#### 정상 작동 확인

모든 명령어를 실행한 후 폴더를 열어보면 설정한 특정 폴더의 파일들만 깔끔하게 다운로드되어 있는 것을 확인할 수 있습니다.

또한 `git remote -v` 명령어로 확인해 보면 처음에 연결했던 원격 저장소가 등록되어 있으며, 이후 파일을 수정하고 `commit` 및 `push` 하는 작업도 기존 Git 사용법과 동일하게 정상 작동합니다.

---

Date: 2026. 03. 15

Tags: Git, GitClone, SparseCheckout, 부분클론, 버전관리, 모노레포, 개발팁, Git최신버전
