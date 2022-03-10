import configparser
import os
import pathlib
import socket
import stat
import zipfile
from xmlrpc import client

import requests

from phases import *


class Core:
    def serverExists(self):
        for p in pathlib.Path(".").rglob("*"):
            if p.name == "TrackmaniaServer":
                return True
        return False

    def downloadServer(self):
        print(
            "It looks like you don't have the server downloaded. Would you like me to get it for you? Please refer to the docs if you have a custom server location. (y/n) ",
            end="",
        )
        while 1:
            i = input()
            if i == "y":
                print("Ok, downloading the server now.")
                req = requests.get(
                    "http://files2.trackmaniaforever.com/TrackmaniaServer_2011-02-21.zip"
                )
                os.mkdir("./server")
                with open("./server/tmp.zip", "wb") as z:
                    z.write(req.content)
                with zipfile.ZipFile("./server/tmp.zip") as z:
                    z.extractall(path="./server")
                os.remove("./server/tmp.zip")
                os.chmod(
                    "./server/TrackmaniaServer",
                    stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH,
                )
                print(
                    "Done downloading the server. Please modify the configuration files as you see fit (and be sure to create a WHITELIST file), then run the program again."
                )
                raise SystemExit
            if i == "n":
                print(
                    "Ok, I won't download the server. Since we have nothing, I am leaving now. Please refer to the docs."
                )
                raise SystemExit

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read("conf.ini")

        if self.config["Main"]["dejavu"] == "y":
            if self.config["Main"]["debug"] == "y":
                print("DEBUG [de]: Deja vu enabled")
            Phases(self.config)
        elif not self.serverExists():
            if self.config["Main"]["debug"] == "y":
                print("DEBUG [do]: And thus God said, let there be a download prompt")
            self.downloadServer()
        else:
            if self.config["Main"]["debug"] == "y":
                print("DEBUG [la]: Launching server")
            Phases(self.config)


if __name__ == "__main__":
    Core()
