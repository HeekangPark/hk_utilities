# JupyterLab Workspace Manager

JupyterLab Workspace를 관리하는 도구

## 설치방법

`jlmanager` 파일을 적절한 위치에 잘 두고 실행하면 됩니다.

### jlmanager.py

`jlmanager`는 `jlmanager.py` 파일을 `pyinstaller`를 이용해 하나의 실행파일로 빌드한 것입니다. 원한다면 `jlmanager.py` 파일을 직접 실행할 수도 있습니다. `jlmanager.py` 실행을 위해서는 다음 패키지가 설치되어 있어야 합니다.

- python 3.8 이상
- jupyter-server
- pyyaml
- tabulate
- hk_utils

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


