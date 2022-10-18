#!/bin/bash
cd $HOME

# download app
rm -rf jlmanager jlmanager-*.tar.gz
wget https://github.com/HeekangPark/utilities/raw/master/jlmanager/jlmanager-latest.tar.gz
tar -zxf jlmanager-latest.tar.gz
mv jlmanager-latest jlmanager
rm -rf jlmanager-latest.tar.gz