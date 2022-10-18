#!/bin/bash
# updater version : 1.0.0

cd $HOME

# download app
rm -rf assh assh-*.tar.gz
wget https://github.com/HeekangPark/utilities/raw/master/assh/assh-latest.tar.gz
tar -zxf assh-latest.tar.gz
rm -rf assh-latest.tar.gz