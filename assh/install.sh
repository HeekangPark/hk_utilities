#!/bin/bash

cd $HOME

rm -rf ~/assh assh.tar.gz
wget https://github.com/HeekangPark/utilities/raw/master/assh/assh.tar.gz
tar -zxf assh.tar.gz
rm assh.tar.gz

mkdir -p scripts
rm -f ~/scripts/assh
ln -s ~/assh/assh ~/scripts/assh
echo 'export PATH=$PATH:$HOME/scripts' >> ~/.bashrc

wget https://github.com/HeekangPark/utilities/raw/master/assh/assh.bash_autocompletion
sudo chown root:root assh.bash_autocompletion
sudo mv assh.bash_autocompletion /etc/bash_completion.d/assh