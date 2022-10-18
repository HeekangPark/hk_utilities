#!/bin/bash
cd $HOME

# download app
rm -rf assh assh-*.tar.gz
wget https://github.com/HeekangPark/utilities/raw/master/assh/assh-latest.tar.gz
tar -zxf assh-latest.tar.gz
mv assh-latest assh
rm -rf assh-latest.tar.gz

# install app (add to ~/scripts)
mkdir -p scripts
rm -f ~/scripts/assh
ln -s $HOME/assh/assh ~/scripts/assh
grep -qxF 'export PATH="$HOME/scripts:$PATH"' ~/.bashrc || echo 'export PATH="$HOME/scripts:$PATH"' >> ~/.bashrc
source ~/.bashrc

# download updater
wget https://raw.githubusercontent.com/HeekangPark/utilities/master/assh/update-assh.sh

# install updater (add to ~/scripts) 
mv update-assh.sh ~/scripts
chmod +x scripts/update-assh.sh

# download bash autocomplete script
wget https://github.com/HeekangPark/utilities/raw/master/assh/assh.bash_autocompletion

# install bash autocomplete script
sudo chown root:root assh.bash_autocompletion
sudo mv assh.bash_autocompletion /etc/bash_completion.d/assh