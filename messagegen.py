class MessageGenerators:
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
