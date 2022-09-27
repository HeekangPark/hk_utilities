#!/bin/bash

rm -rf build dist jlmanager.tar.gz jlmanager.spec

pyinstaller jlmanager.py

# compress tar.gz
cd dist
tar -zvcf jlmanager.tar.gz jlmanager
mv jlmanager.tar.gz ../
cd ../

rm -rf build dist jlmanager.spec
