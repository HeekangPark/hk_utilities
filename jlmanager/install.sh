#!/bin/bash

cd $HOME

rm -rf jlmanager jlmanager.tar.gz
wget https://github.com/HeekangPark/utilities/raw/master/jlmanager/jlmanager.tar.gz
tar -zxf jlmanager.tar.gz
rm jlmanager.tar.gz

mkdir -p scripts
ln -s ~/jlmanager/jlmanager ~/scripts/jlmanager
echo "export PATH=$PATH:$HOME/scripts" >> ~/.bashrc

wget https://github.com/HeekangPark/utilities/raw/master/jlmanager/jlmanager.bash_autocompletion
sudo mv jlmanager.bash_autocompletion /etc/bash_completion.d/jlmanager

