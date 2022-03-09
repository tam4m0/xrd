import socket, os, zipfile, requests, subprocess, time, stat, threading
from xmlrpc import client
from messages import *

class Constants:
    Host = "127.0.0.1"
    Port = 5000
    SuperAdmin = ""
    Prefix = "/"

class Core:
    def downloadServer(self):
        print("It looks like you don't have the server downloaded. Would you like me to get it for you? (y/n) ", end="")
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

    def startServer(self):
        os.chdir("./server")
        self.pPool.append(subprocess.Popen(["./TrackmaniaServer", "/dedicated_cfg=dedicated_cfg.txt", "/internet", "/game_settings=master.txt", "/nodaemon", "/verbose_rpc_full"]))
        time.sleep(10)
        os.chdir("..")

    def phase1(self, host, port):
        with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:
            s.connect((host,int(port)))
            size = int.from_bytes(s.recv(4),'little')
            if(s.recv(size) == "GBXRemote 2".encode()):
                m = Messages(s,self.whitelist)
                m.sendMessage(client.dumps(('SuperAdmin',Constants.SuperAdmin),methodname='Authenticate').encode())
                m.sendMessage(client.dumps((True,),methodname='EnableCallbacks').encode())
                m.sendMessage(client.dumps(("Hello from OpenTM!","",5),methodname="SendNotice").encode())
                print("I got the server up and running.")
                self.phase2(s,m)
            else:
                print("I failed to get the server up and running. Sorry about that, killing the program now.")
                raise SystemExit
                
    def phase2(self, sock, messages):
        messages.listeners[threading.get_native_id()] = []
        while 1:
            data,method = messages.listen(threading.get_native_id())
            if method == "TrackMania.PlayerChat":
                user,cmd,args = self.splitCmd(data,method,"CHAT")
                if cmd == Constants.Prefix + "echo":
                    messages.sendMessage(client.dumps((" ".join(args),user),methodname="ChatSendToLogin").encode())
                if cmd == Constants.Prefix + "hacktheplanet":
                    messages.sendMessage(client.dumps((user,"You've been arrested by the CIA for hacking, GG."),methodname="Kick").encode())
                if cmd == Constants.Prefix + "ban":
                    messages.whiteMessage(client.dumps((args[0],"The ban hammer has spoken!",True),methodname="BanAndBlackList").encode(),user)
            
    def splitCmd(self,data,method,typ):
        if typ == "CHAT":
            user = data[1]
            command = data[2].split(" ")[0]
            args = data[2][1:].split(" ")[1:]
            return(user,command,args)
    
    def __init__(self):
        self.pPool = []
        self.tPool = []

        self.whitelist = []
        
        with open("WHITELIST","r") as f:
            for l in f:
                self.whitelist.append(l)
        
        if not os.path.exists("./server"):
            self.downloadServer()
        else:
            self.startServer()
            self.phase1(Constants.Host,Constants.Port)

if __name__ == "__main__":
    Core()
