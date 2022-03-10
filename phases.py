import socket, os
from messages import *
from messagegen import *
from cmds import *

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
                print("INFO [cn]: I got the connection up and running.")
                self.loop(s,m)
            else:
                print("INFO [dc]: I failed to get the connection up and running. Sorry about that, killing the controller now.")
                raise SystemExit
                
    def loop(self, sock, messages):
        c = Commands(sock,messages,self.config)
        while 1:
            data,method = messages.listen(threading.get_native_id())
            if self.config["Main"]["debug"] == "y":
                print("DEBUG [dm]:",data,method)
            if method == "TrackMania.PlayerConnect":
                user,spec = MessageGenerators.splitCmd(data,method,"CONN")
                print("CONN [co]:",user+(", a spectator," if spec == True else ""),"joined.")
            if method == "TrackMania.PlayerFinish":
                login,timescore = MessageGenerators.splitCmd(data,method,"PEND")
                print("PEND [pe]:",user,"finished with a time of",timescore,"!")
            if method == "TrackMania.PlayerCheckpoint":
                login,timescore,lap,cpindex = MessageGenerators.splitCmd(data,method,"PCHP")
                print("PCHP [pc]:",user,"reached CP",cpindex,"at time",timescore,"!")
            if method == "TrackMania.PlayerChat":
                user,cmd,args = MessageGenerators.splitCmd(data,method,"CHAT")
                if cmd == self.config["Main"]["prefix"] + "echo":
                    c.echo(user,cmd,args)
                if cmd == self.config["Main"]["prefix"] + "hacktheplanet":
                    c.hacktheplanet(user,cmd,args)
                if cmd == self.config["Main"]["prefix"] + "ban":
                    c.ban(user,cmd,args)
                if cmd == self.config["Main"]["prefix"] + "unban":
                    c.unban(user,cmd,args)
                if cmd == self.config["Main"]["prefix"] + "kick":
                    c.kick(user,cmd,args)
                if cmd == self.config["Main"]["prefix"] + "mute":
                    c.mute(user,cmd,args)
                if cmd == self.config["Main"]["prefix"] + "unmute":
                    c.unmute(user,cmd,args)
                if cmd == self.config["Main"]["prefix"] + "forceskip":
                    c.forceskip(user,cmd,args)
                if cmd == self.config["Main"]["prefix"] + "forcerestart":
                    c.forcerestart(user,cmd,args)
                if cmd == self.config["Main"]["prefix"] + "delchall":
                    c.delchall(user,cmd,args)
                if cmd == self.config["Main"]["prefix"] + "updchalls":
                    c.updchalls(user,cmd,args)
                if cmd == self.config["Main"]["prefix"] + "getchalls":
                    c.getchalls(user,cmd,args)
