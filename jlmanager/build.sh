#!/bin/bash

rm -rf build dist jlmanager.tar.gz jlmanager.spec

pyinstaller jlmanager.py

# compress tar.gz
tar -zvcf jlmanager.tar.gz dist/jlmanager

rm -rf build dist jlmanager.spec
