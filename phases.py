from messages import *


class Phases:
    def __init__(self, config):
        self.whitelist = {}

        for p in config["WhiteList"]:
            self.whitelist[p] = config["WhiteList"][p]
        self.config = config
        self.prefix = self.config["Main"]["prefix"]
        self.hostPort = [self.config["HostPort"]["host"], int(self.config["HostPort"]["port"])]


        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.hostPort[0], self.hostPort[1]))
            size = int.from_bytes(s.recv(4), 'little')
            if s.recv(size) == "GBXRemote 2".encode():
                m = Messages(s, self.whitelist)
                m.sendMessage(
                    client.dumps(('SuperAdmin', config["Main"]["superadmin"]), methodname='Authenticate').encode())
                m.sendMessage(client.dumps((True,), methodname='EnableCallbacks').encode())
                m.sendMessage(client.dumps(("Hello from OpenTM!", "", 5), methodname="SendNotice").encode())
                print(f"Established Connection to the server on {self.hostPort[0]}:{self.hostPort[1]}.")
                self.loop(s, m)
            else:
                print(f"I failed to get the connection to {self.hostPort[0]}:{self.hostPort[1]}. Sorry about that, killing the controller now.")
                raise SystemExit

    def loop(self, sock, messages):
        messages.listeners[threading.get_native_id()] = []
        while 1:
            data, method = messages.listen(threading.get_native_id())
            print(data, method)
            if method == "TrackMania.PlayerChat":
                user, cmd, args = self.splitCmd(data, method, "CHAT")
                whitelist = self.getLevel(self.config["WhiteList"][user])


                if cmd == self.prefix + "echo":
                    messages.sendMessage(client.dumps((" ".join(args), user), methodname="ChatSendToLogin").encode())

                if cmd == self.prefix + "hacktheplanet":
                    messages.sendMessage(client.dumps((user, "You've been arrested by the CIA for hacking, GG."), methodname="Kick").encode())

                if cmd == self.prefix + "ban":
                    messages.whiteMessage(client.dumps((args[0], "The ban hammer has spoken!", True), methodname="BanAndBlackList").encode(), user, whitelist, self.getLevel("Operator"))

                if cmd == self.prefix + "unban":
                    messages.whiteMessage(client.dumps((args[0],), methodname="UnBan").encode(), user, whitelist, self.getLevel("Operator"))
                    messages.whiteMessage(client.dumps((args[0],), methodname="UnBlackList").encode(), user, whitelist, self.getLevel("Operator"))

                if cmd == self.prefix + "kick":
                    messages.whiteMessage(client.dumps((args[0], "You've been booted, get out!"), methodname="Kick").encode(), user, self.getLevel(whitelist), self.getLevel("Moderator"))

                if cmd == self.prefix + "mute":
                    messages.whiteMessage(client.dumps((args[0],), methodname="Ignore").encode(), user, whitelist, self.getLevel("Moderator"))

                if cmd == self.prefix + "unmute":
                    messages.whiteMessage(client.dumps((args[0],), methodname="UnIgnore").encode(), user, whitelist, self.getLevel("Moderator"))

    def splitCmd(self, data, method, type):
        if type == "CHAT":
            user = data[1]
            command = data[2].split()[0]
            args = data[2][1:].split()[1:]
            return user, command, args

    def getLevel(self, levelStr):
        if levelStr == "MasterAdmin":
            return 9
        elif levelStr == "Operator":
            return 8
        elif levelStr == "Moderator":
            return 7

