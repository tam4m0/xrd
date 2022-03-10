import threading, os, socket
from messagegen import *
from messages import *
from enums import *

class Commands:
    def __init__(self,sock,messages,config):
        self.sock = sock
        self.config = config
        self.messages = messages
        self.messages.listeners[threading.get_native_id()] = []
    def echo(self,user,cmd,args):
        self.messages.sendMessage(client.dumps((" ".join(args),user),methodname="ChatSendToLogin").encode())
    def hacktheplanet(self,user,cmd,args):
        self.messages.sendMessage(client.dumps((user,"You've been arrested by the CIA for hacking, GG."),methodname="Kick").encode())
    def ban(self,user,cmd,args):
        self.messages.whiteMessage(client.dumps((args[0],"The ban hammer has spoken!",True),methodname="BanAndBlackList").encode(),
                              user,MessageGenerators.getLevel(self.config["WhiteList"][user]),MessageGenerators.getLevel("Operator"))
    def unban(self,user,cmd,args):
        self.messages.whiteMessage(client.dumps((args[0],),methodname="UnBan").encode(),user,
                              PowerLevels[self.config["WhiteList"][user]],PowerLevels.Operator)
        self.messages.whiteMessage(client.dumps((args[0],),methodname="UnBlackList").encode(),user,
                              PowerLevels[self.config["WhiteList"][user]],PowerLevels.Operator)
    def kick(self,user,cmd,args):
        self.messages.whiteMessage(client.dumps((args[0],"You've been booted, get out!"),methodname="Kick").encode(),
                              user,PowerLevels[self.config["WhiteList"][user]],PowerLevels.Moderator)
    def mute(self,user,cmd,args):
        self.messages.whiteMessage(client.dumps((args[0],),methodname="Ignore").encode(),user,
                              PowerLevels[self.config["WhiteList"][user]],PowerLevels.Moderator)
    def unmute(self,user,cmd,args):
        self.messages.whiteMessage(client.dumps((args[0],),methodname="UnIgnore").encode(),user,
                              PowerLevels[self.config["WhiteList"][user]],PowerLevels.Moderator)
    def forceskip(self,user,cmd,args):
        self.messages.whiteMessage(client.dumps(tuple(),methodname="NextChallenge").encode(),user,
                              PowerLevels[self.config["WhiteList"][user]],PowerLevels.Moderator)
    def forcerestart(self,user,cmd,args):
        self.messages.whiteMessage(client.dumps(tuple(),methodname="RestartChallenge").encode(),user,
                              PowerLevels[self.config["WhiteList"][user]],PowerLevels.Moderator)
    def delchall(self,user,cmd,args):
        self.messages.whiteMessage(client.dumps((args[0],),methodname="RemoveChallenge").encode(),user,
                              PowerLevels[self.config["WhiteList"][user]],PowerLevels.Operator)
    def updchalls(self,user,cmd,args):
        try:
            if user in self.whitelist.keys():
                if self.config["WhiteList"][user] >= PowerLevels.Operator:
                    if os.path.exists(self.config["Main"]["tracksfolder"]):
                        for r,d,f in os.walk(self.config["Main"]["tracksfolder"]):
                            for n in f:
                                if self.config["Main"]["debug"] == "y":
                                    print("DEBUG [tr]:",n)
                                else:
                                    self.messages.sendMessage(client.dumps(("There is no tracksfolder defined in the configuration. Please try again after defining this and restarting the server controller.",user),methodname="ChatSendToLogin").encode())
        except Exception as e:
            self.messages.sendMessage(client.dumps(("Unknown error occurred. Please try again.",user),methodname="ChatSendToLogin").encode())
    def getchalls(self,user,cmd,args):
        try:
            if os.path.exists(self.config["Main"]["tracksfolder"]):
                for r,d,f in os.walk(self.config["Main"]["tracksfolder"]):
                    for n in f:
                        self.messages.sendMessage(client.dumps((n,),methodname="ChatSendToLogin").encode())
                    else:
                        self.messages.sendMessage(client.dumps(("There is no tracksfolder defined in the configuration. Please try again after defining this and restarting the server controller.",user),methodname="ChatSendToLogin").encode())
        except Exception as e:
            self.messages.sendMessage(client.dumps(("Unknown error occurred. Please try again.",user),methodname="ChatSendToLogin").encode())
