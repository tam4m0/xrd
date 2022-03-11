# This file is part of xrd.
#
# xrd is free software: you can redistribute it and/or modify it under the terms of
# the GNU General Public License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.
#
# xrd is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with xrd.
# If not, see <https://www.gnu.org/licenses/>.

all: pre format pyinstaller rename last

pre:
	python Makefile.py

format:
	black *.py
	black ./plugins/*.py
	isort --profile black *.py
	isort --profile black ./plugins/*.py

pyinstaller:
	pyinstaller --onefile --clean ./Makefile.spec

rename:
	mv dist/cmds dist/xrd

last:
	echo "Your build of xrd is ready as ./dist/xrd"
