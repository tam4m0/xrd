from math import floor

class MessageGenerators:
    def splitCmd(data,method,typ):
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

    def timestrToHMS(timestr):
        s = int(timestr)/1000
        m = s/60
        s %= 60
        h = m/60
        m %= 60
        return str(floor(h))+"h"+str(floor(m))+"m"+str(round(s,2))+"s"
