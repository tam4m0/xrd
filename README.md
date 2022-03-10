# xrd (XASeCo Replacing Daemon)

xrd is a next-gen server controller for TrackMania Forever that is designed to be hassle-free and easily updatable (with a bus factor of 0).

[![CodeQL](https://github.com/AomegaL/xrd/actions/workflows/codeql-analysis.yml/badge.svg?branch=main)](https://github.com/AomegaL/xrd/actions/workflows/codeql-analysis.yml)
<a href="https://discord.gg/5DT5Vs2ZHS">
  <img src="https://discordapp.com/api/guilds/951272271266344960/widget.png?style=shield"/>
</a>
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.0-4baaaa.svg)](CODE_OF_CONDUCT.md) 

<img src="https://i.arxius.io/8c526630.png"/>

# Building

xrd enjoys being made mostly out of stdlib code, so you do not need to install dependencies for the program itself to run (yet). <br/>
However, if you do want to run the static build without downloading a release, you'll need to build it. <br/>
Just run GNU Make inside the git directory to produce a static build of xrd (provided you have pyinstaller and upx installed). <br/>

# Running

Just point a Python interpreter to `init.py` or point a command prompt to the PyInstaller executable.
