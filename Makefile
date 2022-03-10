all: format pyinstaller rename last

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