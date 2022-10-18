#!/bin/bash
            cd $HOME

            rm -rf assh assh-*.tar.gz
            wget https://github.com/HeekangPark/utilities/raw/master/assh/assh-latest.tar.gz
            tar -zxf assh-latest.tar.gz
            mv assh-latest assh
            rm -rf assh-latest.tar.gz

            mkdir -p scripts
            rm -f ~/scripts/assh
            ln -s $HOME/assh/assh ~/scripts/assh
            grep -qxF 'export PATH=$PATH:$HOME/scripts' ~/.bashrc || echo 'export PATH=$PATH:$HOME/scripts' >> ~/.bashrc
            source ~/.bashrc

            wget https://raw.githubusercontent.com/HeekangPark/utilities/master/assh/update-assh.sh
            mv update-assh.sh ~/scripts
            chmod +x scripts/update-assh.sh

            wget https://github.com/HeekangPark/utilities/raw/master/assh/assh.bash_autocompletion
            sudo chown root:root assh.bash_autocompletion
            sudo mv assh.bash_autocompletion /etc/bash_completion.d/assh
        