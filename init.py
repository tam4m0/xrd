import socket, os, zipfile, requests, pathlib, stat, configparser
from xmlrpc import client
from phases import *

class Core:
    def serverExists(self):
        for p in pathlib.Path(".").rglob("*"):
            if p.name == "TrackmaniaServer":
                return True
        return False
    
    def downloadServer(self):
        print("It looks like you don't have the server downloaded. Would you like me to get it for you? If it's in another location outside of the current directory, please type n here! (y/n) ", end="")
        while 1:
            i = input()
            if i == "y":
                print("Ok, downloading the server now.")
                req = requests.get("http://files2.trackmaniaforever.com/TrackmaniaServer_2011-02-21.zip")
                os.mkdir("./server")
                with open('./server/tmp.zip', 'wb') as z:
                    z.write(req.content)
                with zipfile.ZipFile('./server/tmp.zip') as z:
                    z.extractall(path="./server")
                os.remove('./server/tmp.zip')
                os.chmod('./server/TrackmaniaServer',stat.S_IXUSR|stat.S_IXGRP|stat.S_IXOTH)
                print("Done downloading the server. Please modify the configuration files as you see fit (and be sure to create a WHITELIST file), then run the program again.")
                raise SystemExit
            if i == "n":
                print("Ok, I won't download the server. Since we have nothing, I am leaving now. Please refer to the docs.")
                raise SystemExit

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read("conf.ini")

        if not self.serverExists():
            self.downloadServer()
        else:
            Phases(self.config)

if __name__ == "__main__":
    Core()
