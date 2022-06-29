#!/bin/bash

# ~/scripts 디렉토리를 만들고, 본 repository의 assh 파일을 복사한 후, 실행 권한을 부여한다.
mkdir -p ~/scripts
cp assh ~/scripts/
chmod +x ~/scripts/assh

# ~/.bashrc 파일에 export PATH="$HOME/scripts:$PATH" 행을 추가한다.
echo "export PATH=\"\$HOME/scripts:\$PATH\"" >> ~/.bashrc

# /etc/bash_completion.d 디렉토리에 본 repository의 assh.bash.autocomplete 파일을 assh라는 이름으로 복사한다(관리자 권한 필요).
sudo cp assh.bash.autocomplete /etc/bash_completion.d/assh