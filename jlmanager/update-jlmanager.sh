#!/bin/bash
# updater version : 1.0.0

cd $HOME

# download app
rm -rf jlmanager jlmanager-*.tar.gz
wget https://github.com/HeekangPark/utilities/raw/master/jlmanager/jlmanager-latest.tar.gz
tar -zxf jlmanager-latest.tar.gz
rm -rf jlmanager-latest.tar.gz