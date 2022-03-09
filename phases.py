import socket
from messages import *

class Phases:
    def __init__(self, config):
        self.whitelist = {}
        for p in config["WhiteList"]:
            self.whitelist[p] = config["WhiteList"][p]
        self.config = config
        with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:
            s.connect((self.config["HostPort"]["host"],int(self.config["HostPort"]["port"])))
            size = int.from_bytes(s.recv(4),'little')
            if(s.recv(size) == "GBXRemote 2".encode()):
                m = Messages(s,self.whitelist)
                m.sendMessage(client.dumps(('SuperAdmin',config["Main"]["superadmin"]),methodname='Authenticate').encode())
                m.sendMessage(client.dumps((True,),methodname='EnableCallbacks').encode())
                m.sendMessage(client.dumps(("Hello from OpenTM!","",5),methodname="SendNotice").encode())
                print("I got the connection up and running.")
                self.loop(s,m)
            else:
                print("I failed to get the connection up and running. Sorry about that, killing the controller now.")
                raise SystemExit
                
    def loop(self, sock, messages):
        messages.listeners[threading.get_native_id()] = []
        while 1:
            data,method = messages.listen(threading.get_native_id())
            if method == "TrackMania.PlayerChat":
                user,cmd,args = self.splitCmd(data,method,"CHAT")
                if cmd == self.config["Main"]["prefix"] + "echo":
                    messages.sendMessage(client.dumps((" ".join(args),user),methodname="ChatSendToLogin").encode())
                if cmd == self.config["Main"]["prefix"] + "hacktheplanet":
                    messages.sendMessage(client.dumps((user,"You've been arrested by the CIA for hacking, GG."),methodname="Kick").encode())
                if cmd == self.config["Main"]["prefix"] + "ban":
                    messages.whiteMessage(client.dumps((args[0],"The ban hammer has spoken!",True),methodname="BanAndBlackList").encode(),user)
            
    def splitCmd(self,data,method,typ):
        if typ == "CHAT":
            user = data[1]
            command = data[2].split(" ")[0]
            args = data[2][1:].split(" ")[1:]
            return(user,command,args)