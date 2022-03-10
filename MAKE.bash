#!/bin/bash

# pyinstaller does all the work for us, compressing
# all the files into one py executable
#
# if you're a contributor, make sure to install upx
pyinstaller --onefile *.py

# what's likely in there is xrd masquerading as another
# python file, so we're moving it
mv dist/cmds dist/xrd

echo "Your build of xrd is ready as ./dist/xrd"
