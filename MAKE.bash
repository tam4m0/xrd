#!/bin/bash

# pyinstaller does all the work for us, compressing all the files into one py executable
# if you're a contributor, make sure to install upx
pyinstaller --onefile *.py

# we don't know what's in there, but we're assuming it's the file we built
mkdir build
mv dist/* build
