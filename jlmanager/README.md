# JupyterLab Workspace Manager

JupyterLab Workspace를 관리하는 도구

## 실행방법

아래 네 가지 방법 중 아무거나 선택해서 실행하면 됩니다.

### 설치 스크립트 이용 (install.sh) [Most Recommended]

아래 "다중 파일" 설치를 자동적으로 수행합니다.

구체적으로, 다음 동작을 수행합니다.

1. 홈 디렉토리에서 `jlmanager.tar.gz` 파일의 압축을 해제하여 `~/jlmanager` 디렉토리를 생성합니다.
2. `~/scripts` 디렉토리를 생성하고, `PATH` 환경변수에 추가합니다.
3. `~/scripts` 디렉토리에 `~/jlmanager/jlmanager` 파일의 심볼릭 링크를 생성합니다.
4. `/etc/bash_completion.d` 디렉토리에 자동완성을 위한 스크립트를 등록합니다(sudo 필요).

### jlmanager.py

`jlmanager.py`를 직접 실행합니다.

```bash
python jlmanager.py <command> [options]
```

`jlmanager.py` 실행을 위해서는 다음 패키지가 설치되어 있어야 합니다.

- python 3.8 이상
- jupyter-server
- pyyaml
- tabulate
- hk_utils

### 다중 파일 [Most Recommended]

`jlmanager.tar.gz` 파일은 `pyinstaller`를 이용해 `jlmanager.py`를 패키징한 후, 디렉토리를 압축한 것입니다. 압축을 풀면 추가적인 패키지를 설치할 필요 없이 바로 실행 가능합니다.

```bash
tar -xvf jlmanager.tar.gz  # 압축 풀기
cd jlmanager
./jlmanager <command> [options]
```

### 단일 파일

`jlmanager` 파일은 `pyinstaller`를 이용해 `jlmanager.py`를 단일 파일로 패키징한 것입니다. 추가적인 패키지를 설치할 필요 없이 바로 실행 가능합니다. 단, 세 가지 방법 중 가장 느립니다.

```bash
./jlmanager <command> [options]
```

## 사용법

### workspace 생성

```bash
jlmanager create <workspace_name>
```

- `workspace_name` : 생성할 workspace 이름

새로운 workspace를 생성합니다.

구체적으로, 다음 동작을 수행합니다.

1. 새로운 conda environment를 생성하고, jupyterlab 패키지를 설치합니다.
2. 새로운 directory를 생성합니다. (default: `~/workspace` 밑에 `workspace_name` 이름으로 생성)

### workspace 삭제

```bash
jlmanager delete <workspace_name>
```

- `workspace_name` : 삭제할 workspace 이름

workspace를 삭제합니다.

구체적으로, 다음 동작을 수행합니다.

1. conda environment를 삭제합니다.
2. directory를 삭제합니다.

### workspace 목록 확인

```bash
jlmanager list [-v]
```

- `-v` : 더 자세한 정보를 볼 수 있습니다.

현재 생성된 workspace 목록을 확인합니다.

```
jlmanager list --running [-v]
```

- `-v` : 더 자세한 정보를 볼 수 있습니다.

현재 jupyterlab을 실행 중인 workspace 목록을 확인합니다.

### jupyterlab 실행

```bash
jlmanager run <workspace_name>
```

- `workspace_name` : 실행할 workspace 이름

workspace를 실행합니다.

### jupyterlab 종료

```bash
jlmanager stop <workspace_name>
```

- `workspace_name` : 종료할 workspace 이름

workspace를 종료합니다.

### 도움말

```bash
jlmanager --help
jlmanager <command> --help
```

- `command` : "create", "delete", "list", "run", "stop"

도움말을 확인합니다.


