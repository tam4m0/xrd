import configparser
import os

config = configparser.ConfigParser()
config.read("conf.ini")
config["Plugins"]["workdir"] = os.getcwd()
with open("conf.ini", "w") as f:
    config.write(f)
