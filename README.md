# xrd (XASeCo Replacing Daemon)

xrd is a next-gen server controller for TrackMania Forever that is designed to be hassle-free and easily updatable (with a bus factor of 0).

[![CodeQL](https://github.com/AomegaL/xrd/actions/workflows/codeql-analysis.yml/badge.svg?branch=main)](https://github.com/AomegaL/xrd/actions/workflows/codeql-analysis.yml)
<a href="https://discord.gg/5DT5Vs2ZHS">
  <img src="https://discordapp.com/api/guilds/951272271266344960/widget.png?style=shield"/>
</a>
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.0-4baaaa.svg)](CODE_OF_CONDUCT.md) 

<img src="https://i.arxius.io/8c526630.png"/>

# Building

xrd enjoys being made mostly out of stdlib code, and you do not need to `make` the code. <br/>
However, if you do want a single file, you'll need to build plugins inside of the executable. <br/>
Just run GNU Make inside the git directory to produce a static build of xrd (provided you have pyinstaller and upx installed). <br/>

# Running

Point a command prompt to the PyInstaller executable. Easy as that, the plugins are built into the executable!

/updplugins is only usable if you have kept the git directory, have `make`d the program before, and are running inside of the `dist` folder. It's sort of an afterthought...
