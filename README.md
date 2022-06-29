# Advanced SSH by Heekang Park

OpenSSH 클라이언트에 다음 추가적인 기능을 붙인 SSH Client

## Advanced SSH의 장/단점

**장점**

- 기존 SSH config file에서보다 훨씬 간결하고 효율적인 문법으로 config file을 작성할 수 있다.
- local port forwarding을 간단한 문법으로 바로 만들 수 있다.

**단점**

- config file에 작성되지 않은 Host에 접속할 경우 사용하기 어렵다.
    - config file에 작성되지 않은 Host에 접속할 경우 그냥 ssh 명령어로 바로 접속하는 것을 추천한다.


## 설치 요구사항

- Linux (Ubuntu, WSL에서 시험됨)
- 시스템에 python 3이 설치되어 있고, `/usr/bin/python3`으로 실행할 수 있어야 한다.

Bash 쉘을 사용하는 경우 자동완성 기능을 사용할 수 있다. 자동완성 기능을 사용하려면 다음 요구사항이 만족되어야 한다.

- Bash 권한을 사용할 수 있어야 한다.
- 관리자 권한을 사용할 수 있어야 한다.

## 설치 방법

### 전체 설치

1. 본 repository를 clone한다.
    ```
    git clone https://github.com/HeekangPark/assh
    ```

2. `install.sh` 스크립트를 실행한다. 
    ```
    ./install.sh
    ```
    이 스크립트는 다음 동작을 수행한다.
    1. `~/scripts` 디렉토리를 만들고, 본 repository의 `assh` 파일을 복사한 후, 실행 권한을 부여한다.
    2. `~/.bashrc` 파일에 `export PATH="$HOME/scripts:$PATH"` 행을 추가한다.
    3. `/etc/bash_completion.d` 디렉토리에 본 repository의 `assh.bash.autocomplete` 파일을 `assh`라는 이름으로 복사한다(관리자 권한 필요).

3. 사용중인 쉘을 종료했다가 다시 로그인한다. 다음 명령어를 입력해 `assh`가 정상적으로 설치되었는지 확인한다. `assh` 버전이 출력되면 정상적으로 설치가 완료된 것이다.
    ```
    assh --version
    ```

### 최소 설치

만약 자동완성 기능을 사용하고 싶지 않다면 본 repository의 `assh.py` 파일만 적당히 복사해 사용하면 된다.

## 사용 방법

### Advanced SSH config file 작성법

- config file은 다음과 같은 형태의 `Host`들이 여럿 모여 있는 파일이다.
    ```yaml
    @<annotation>
    ...
    Host: <host1> <host2> ...
      Hostname: <hostname>
      User: <user>
      Port: <port>
      ...
    ```
- `Host`는 다음 규칙을 따른다.
    - `Host: <host명>` 형태로 작성한다. 띄어쓰기로 구분하여 여러 개의 Host들을 한 번에 작성할 수도 있다.
    - 아무런 indentation 없이 작성되어야 한다.
    - Host명은 Advanced SSH config file 전체에서 unique해야 한다.
        - 같은 이름을 가진 Host가 있으면 병합된다.
    - Host 위에는 annotation을 추가할 수도 있다.
        - annotation은 `@`으로 시작하고, indentation이 없어야 한다.
        - 현재 사용 가능한 annotation으로는 `@useDefault`가 있다.

- `Host`의 하위 옵션들은 다음 규칙을 따른다.
    - `Host` 바로 아래에서 한 칸 이상의 indentation을 가지고 `key: value` 형태로 작성되어야 한다.
    - key, value는 SSH config 파일에서의 그것들과 같다. 다만 key와 value를 구분할 때 공백이 아닌 colon(`:`)을 사용한다.
    - `HostName`의 경우 명시되지 않으면 `Host`와 동일한 값을 사용한다.
    - `User`의 경우 명시되지 않으면 현재 로그인한 사용자의 이름을 사용한다.
    - `Port`의 경우 명시되지 않으면 "22"를 사용한다.
    - value에는 `{{   }}` interpolation을 사용할 수 있다. 
        - `{{   }}` 안에는 간단한 python 코드를 작성할 수 있다. 이때 이때 python 코드는 문자열(str)을 반환해야 한다. 
        - `{{   }}` 안에서는 `re`, `os` 패키지를 제외한 모든 패키지는 사용할 수 없다.
        - `{{   }}` 안에서는 `Host`와 다른 옵션들을 변수명으로 사용할 수 있다.
        - 예를 들어, `{{ Host[:2] }}`라 하면 `Host`의 앞 2글자를 사용하는 것이다.

- `default`를 사용할 수 있다.
    ```yaml
    default:
      Hostname: <hostname>
      User: <user>
      Port: <port>
      ...
    ```
    - `default`에는 모든 Host에 공통적으로 적용되는 옵션을 설정할 수 있다.
    - 특정 Host에서 `default`에 있는 값들을 사용하고 싶으면 `@useDefault` annotation을 `Host` 위에 달면 된다.
        - 만약 Host에서 직접 지정한 옵션이 default의 항목과 충돌한다면 Host에서 직접 지정한 옵션이 우선시된다.

- 한 줄 주석(one-line comment)을 사용할 수 있다.
    - 주석은 `#`으로 시작한다.
    - 주석 앞에는 indentation이 몇 칸이든 올 수 있다.

- 다음은 Advanced SSH config file 예시이다.

    ```yaml
    default:
      User: heekang
      PreferredAuthentications: publickey
      ServerAliveInterval: 120
      ServerAliveCountMax: 5
      IdentityFile: ~/.ssh/{{ Host }}
    
    @useDefault
    Host: phk-home-server
      HostName: 1.2.3.4
    
    @useDefault
    Host: server10 server11
      HostName: 5.6.7.8
      Port: {{ Host[2:] }}
    
    @useDefault
    Host: server13 server14 server15 server16
      HostName: 9.10.11.12
      Port: 22{{ Host[2:] }}
      IdentityFile: ~/.ssh/clusters
    ```

### Advanced SSH 사용법

#### Host에 접속하기

```bash
assh [-f|--file <config_file>] connect <host> [SSH options]
```

- `-f, --file <config_file>` : Advanced SSH config file 경로를 명시한다. 만약 아무런 값도 주어지지 않으면 `~/.assh.config` 경로가 사용된다.
- `host` : 접속할 Host명.
    - 만약 Host명이 Advanced SSH config file에 없다면 접속 오류가 발생한다.
    - Host명 뒤에 `.`을 붙여 추가적인 옵션을 줄 수 있다.
        - `Lxx`를 붙이면 localhost의 xx 포트와 서버의 xx 포트에 대해 Local Port Forwarding을 건다. 예를 들어, `server1.L8080`이라 하면 server1의 8080 포트와 localhost의 8080 포트를 local port forwarding 한다(`-L 8080:localhost:8080`과 동일한 효과).
- `SSH options` : SSH 옵션을 추가할 수 있다.

#### 모든 Host 출력하기

```bash
assh [-f|--file <config_file>] -l
assh [-f|--file <config_file>] --list
```

- `-f, --file <config_file>` : Advanced SSH config file 경로를 명시한다. 만약 아무런 값도 주어지지 않으면 `~/.assh.config` 경로가 사용된다.

참고
- bash 자동완성을 위해 이 명령어가 사용된다.
- 이 명령어를 이용하면 Advanced SSH config file이 제대로 작성되었는지 간단히 검증할 수 있다. 만약 내가 접속하고자 하는 Host가 이 명령어의 출력에 없다면 Advanced SSH config file 작성에 뭔가 문제가 있는 것이다.

#### SSH config file 업데이트하기

```bash
assh [-f|--file <config_file>] --update-ssh-config-file [--overwrite]
```

- `-f, --file <config_file>` : Advanced SSH config file 경로를 명시한다. 만약 아무런 값도 주어지지 않으면 `~/.assh.config` 경로가 사용된다.
- `--overwrite` : 
    - SSH config file(`~/.ssh/config`)이 존재하지 않는 경우, `--overwrite` 옵션은 무시된다; 항상 Advanced SSH config file로부터 SSH config file을 새로 만든다.
    - SSH config file이 존재하는 경우,
        - `--overwrite` 옵션이 사용된 경우, 기존 SSH config file을 `~/.ssh/config.old` 파일로 백업해놓고, Advanced SSH config file로부터 SSH config file을 새로 만든다.
        - `--overwrite` 옵션이 사용되지 않은 경우, 아무런 동작도 하지 않고 프로그램이 종료된다.

#### 도움말, 버전 확인하기

```bash
assh -h
assh --help
assh -v
assh --version
```