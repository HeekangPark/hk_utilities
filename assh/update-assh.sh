#!/bin/bash
cd $HOME

# download app
rm -rf assh assh-*.tar.gz
wget https://github.com/HeekangPark/utilities/raw/master/assh/assh-latest.tar.gz
tar -zxf assh-latest.tar.gz
mv assh-latest assh
rm -rf assh-latest.tar.gz