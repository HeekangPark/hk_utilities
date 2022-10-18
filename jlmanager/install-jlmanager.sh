#!/bin/bash
# installer version : 1.0.0

cd $HOME

# download app
rm -rf jlmanager jlmanager-*.tar.gz
wget https://github.com/HeekangPark/utilities/raw/master/jlmanager/jlmanager-latest.tar.gz
tar -zxf jlmanager-latest.tar.gz
rm -rf jlmanager-latest.tar.gz

# install app (add to ~/scripts)
mkdir -p scripts
rm -f ~/scripts/jlmanager
ln -s $HOME/jlmanager/jlmanager ~/scripts/jlmanager
grep -qxF 'export PATH="$HOME/scripts:$PATH"' ~/.bashrc || echo 'export PATH="$HOME/scripts:$PATH"' >> ~/.bashrc
source ~/.bashrc

# download updater
wget https://raw.githubusercontent.com/HeekangPark/utilities/master/jlmanager/update-jlmanager.sh

# install updater (add to ~/scripts) 
mv update-jlmanager.sh ~/scripts
chmod +x scripts/update-jlmanager.sh

# download bash autocomplete script
wget https://github.com/HeekangPark/utilities/raw/master/jlmanager/jlmanager.bash_autocompletion

# install bash autocomplete script
sudo chown root:root jlmanager.bash_autocompletion
sudo mv jlmanager.bash_autocompletion /etc/bash_completion.d/jlmanager