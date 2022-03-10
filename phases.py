import socket, os
from messages import *
from messagegen import *
from cmds import *


class Phases:
    def __init__(self, config):
        print(
            """
     ,..........         ...........    
     .':cccccc:;.       .;ccccccc:,.    
       .;ccccccc:'.    .;:cc:::::'.     
        .;ccccccc:'.  .:cclcccc;.       
         .,::::::::;,;ccccllol:.        
           .;cccccccccccldxkxc.         
            .:looolllodxkOOd:.          
            .;dOOkkkkOOOOko;.           
            .cxkOOOOOOkxo:,'.           
           .;llllodddoc;,.....          
         .,okOOko:;,....,;codl,.        
        .;x0KKK0Od;. ..cdkO0K0d;.       
       .;d0K0K00kc.   .ck000KK0x:..     
      /:d0KKK00x;.     .;x00KKK0Oxl\    
    .;ldxkkkkxo,         ,oxkkkkkkxl,   
     ..........           ..........  
                           xrd v0.1.0
"""
        )
        self.whitelist = {}
        for p in config["WhiteList"]:
            self.whitelist[p] = config["WhiteList"][p]
        self.config = config
        self.prefix = config["Main"]["prefix"]
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(
                (self.config["HostPort"]["host"], int(self.config["HostPort"]["port"]))
            )
            size = int.from_bytes(s.recv(4), "little")
            if s.recv(size) == "GBXRemote 2".encode():
                m = Messages(s, self.whitelist)
                m.sendMessage(
                    client.dumps(
                        ("SuperAdmin", config["Main"]["superadmin"]),
                        methodname="Authenticate",
                    ).encode()
                )
                m.sendMessage(
                    client.dumps((True,), methodname="EnableCallbacks").encode()
                )
                m.sendMessage(
                    client.dumps(
                        ("Hello from xrd!", "", 5), methodname="SendNotice"
                    ).encode()
                )
                print("INFO [cn]: I got the connection up and running.")
                self.loop(s, m)
            else:
                print(
                    "INFO [dc]: I failed to get the connection up and running. Sorry about that, killing the controller now."
                )
                raise SystemExit

    def loop(self, sock, messages):
        c = Commands(sock, messages, self.config)
        while 1:
            data, method = messages.listen(threading.get_native_id())
            if self.config["Main"]["debug"] == "y":
                print("DEBUG [dm]:", data, method)
            if method == "TrackMania.PlayerConnect":
                user, spec = MessageGenerators.splitCmd(data, method, "CONN")
                print(
                    "CONN [co]:",
                    user + (", a spectator," if spec == True else ""),
                    "joined.",
                )
            if method == "TrackMania.PlayerFinish":
                login, timescore = MessageGenerators.splitCmd(data, method, "PEND")
                if timescore == 0:
                    pass
                else:
                    print(
                        "PEND [pe]:",
                        login,
                        "finished with a time of",
                        MessageGenerators.timestrToHMS(timescore) + "!",
                    )
            if method == "TrackMania.PlayerCheckpoint":
                login, timescore, lap, cpindex = MessageGenerators.splitCmd(
                    data, method, "PCHP"
                )
                if timescore == 0:
                    pass
                else:
                    print(
                        "PCHP [pc]:",
                        login,
                        "reached CP",
                        cpindex,
                        "at time",
                        MessageGenerators.timestrToHMS(timescore) + "!",
                    )
            if method == "TrackMania.PlayerChat":
                user, cmd, args = MessageGenerators.splitCmd(data, method, "CHAT")
                if cmd == self.prefix + "echo":
                    c.echo(user, cmd, args)
                if cmd == self.prefix + "hacktheplanet":
                    c.hacktheplanet(user, cmd, args)
                if cmd == self.prefix + "ban":
                    c.ban(user, cmd, args)
                if cmd == self.prefix + "unban":
                    c.unban(user, cmd, args)
                if cmd == self.prefix + "kick":
                    c.kick(user, cmd, args)
                if cmd == self.prefix + "mute":
                    c.mute(user, cmd, args)
                if cmd == self.prefix + "unmute":
                    c.unmute(user, cmd, args)
                if cmd == self.prefix + "forceskip":
                    c.forceskip(user, cmd, args)
                if cmd == self.prefix + "forcerestart":
                    c.forcerestart(user, cmd, args)
                if cmd == self.prefix + "delchall":
                    c.delchall(user, cmd, args)
                if cmd == self.prefix + "updchalls":
                    c.updchalls(user, cmd, args)
                if cmd == self.prefix + "getchalls":
                    c.getchalls(user, cmd, args)
