import socket, os
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
                print("INFO [cn]: I got the connection up and running.")
                self.loop(s,m)
            else:
                print("INFO [dc]: I failed to get the connection up and running. Sorry about that, killing the controller now.")
                raise SystemExit
                
    def loop(self, sock, messages):
        messages.listeners[threading.get_native_id()] = []
        while 1:
            data,method = messages.listen(threading.get_native_id())
            if self.config["Main"]["debug"] == "y":
                print("DEBUG [dm]:",data,method)
            if method == "TrackMania.PlayerConnect":
                user,spec = self.splitCmd(data,method,"CONN")
                print("CONN [co]:",user+(", a spectator," if spec == True else ""),"joined.")
            if method == "TrackMania.PlayerFinish":
                login,timescore = self.splitCmd(data,method,"PEND")
                print("PEND [pe]:",user,"finished with a time of",timescore,"!")
            if method == "TrackMania.PlayerCheckpoint":
                login,timescore,lap,cpindex = self.splitCmd(data,method,"PCHP")
                print("PCHP [pc]:",user,"reached CP",cpindex,"at time",timescore,"!")
            if method == "TrackMania.PlayerChat":
                user,cmd,args = self.splitCmd(data,method,"CHAT")
                if cmd == self.config["Main"]["prefix"] + "echo":
                    messages.sendMessage(client.dumps((" ".join(args),user),methodname="ChatSendToLogin").encode())
                if cmd == self.config["Main"]["prefix"] + "hacktheplanet":
                    messages.sendMessage(client.dumps((user,"You've been arrested by the CIA for hacking, GG."),methodname="Kick").encode())
                if cmd == self.config["Main"]["prefix"] + "ban":
                    messages.whiteMessage(client.dumps((args[0],"The ban hammer has spoken!",True),methodname="BanAndBlackList").encode(),user,self.getLevel(self.config["WhiteList"][user]),self.getLevel("Operator"))
                if cmd == self.config["Main"]["prefix"] + "unban":
                    messages.whiteMessage(client.dumps((args[0],),methodname="UnBan").encode(),user,self.getLevel(self.config["WhiteList"][user]),self.getLevel("Operator"))
                    messages.whiteMessage(client.dumps((args[0],),methodname="UnBlackList").encode(),user,self.getLevel(self.config["WhiteList"][user]),self.getLevel("Operator"))
                if cmd == self.config["Main"]["prefix"] + "kick":
                    messages.whiteMessage(client.dumps((args[0],"You've been booted, get out!"),methodname="Kick").encode(),user,self.getLevel(self.config["WhiteList"][user]),self.getLevel("Moderator"))
                if cmd == self.config["Main"]["prefix"] + "mute":
                    messages.whiteMessage(client.dumps((args[0],),methodname="Ignore").encode(),user,self.getLevel(self.config["WhiteList"][user]),self.getLevel("Moderator"))
                if cmd == self.config["Main"]["prefix"] + "unmute":
                    messages.whiteMessage(client.dumps((args[0],),methodname="UnIgnore").encode(),user,self.getLevel(self.config["WhiteList"][user]),self.getLevel("Moderator"))
                if cmd == self.config["Main"]["prefix"] + "forceskip":
                    messages.whiteMessage(client.dumps(tuple(),methodname="NextChallenge").encode(),user,self.getLevel(self.config["WhiteList"][user]),self.getLevel("Moderator"))
                if cmd == self.config["Main"]["prefix"] + "forcerestart":
                    messages.whiteMessage(client.dumps(tuple(),methodname="RestartChallenge").encode(),user,self.getLevel(self.config["WhiteList"][user]),self.getLevel("Moderator"))
                if cmd == self.config["Main"]["prefix"] + "delchall":
                    messages.whiteMessage(client.dumps((args[0],),methodname="RemoveChallenge").encode(),user,self.getLevel(self.config["WhiteList"][user]),self.getLevel("Operator"))
                if cmd == self.config["Main"]["prefix"] + "updchalls":
                    try:
                        if user in self.whitelist.keys():
                            if self.getLevel(self.config["WhiteList"][user]) >= self.getLevel("Operator"):
                                if os.path.exists(self.config["Main"]["tracksfolder"]):
                                    for r,d,f in os.walk(self.config["Main"]["tracksfolder"]):
                                        for n in f:
                                            if self.config["Main"]["debug"] == "y":
                                                print("DEBUG [tr]:",n)
                                else:
                                    messages.sendMessage(client.dumps(("There is no tracksfolder defined in the configuration. Please try again after defining this and restarting the server controller.",user),methodname="ChatSendToLogin").encode())
                    except Exception as e:
                        messages.sendMessage(client.dumps(("Unknown error occurred. Please try again.",user),methodname="ChatSendToLogin").encode())
                if cmd == self.config["Main"]["prefix"] + "getchalls":
                    try:
                        if os.path.exists(self.config["Main"]["tracksfolder"]):
                            for r,d,f in os.walk(self.config["Main"]["tracksfolder"]):
                                for n in f:
                                    messages.sendMessage(client.dumps((n,),methodname="ChatSendToLogin").encode())
                        else:
                            messages.sendMessage(client.dumps(("There is no tracksfolder defined in the configuration. Please try again after defining this and restarting the server controller.",user),methodname="ChatSendToLogin").encode())
                    except Exception as e:
                        messages.sendMessage(client.dumps(("Unknown error occurred. Please try again.",user),methodname="ChatSendToLogin").encode())

    def splitCmd(self,data,method,typ):
        if typ == "CHAT":
            user = data[1]
            command = data[2].split(" ")[0]
            args = data[2][1:].split(" ")[1:]
            return(user,command,args)
        if typ == "CONN":
            login = data[0]
            spec = data[1]
            return(login,spec)
        if typ == "PEND":
            login = data[1]
            timescore = data[2]
            return(login,timescore)
        if typ == "PCHP":
            login = data[1]
            timescore = data[2]
            lap = data[3]
            cpindex = data[4]
            return(login,timescore,lap,cpindex)

    def getLevel(self,levelStr):
        if levelStr == "MasterAdmin":
            return 9
        elif levelStr == "Operator":
            return 8
        elif levelStr == "Moderator":
            return 7
