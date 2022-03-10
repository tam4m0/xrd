from cmds import *
from messagegen import *


class Main:
    def __init__(self, socket, messages, config):
        c = Commands(socket, messages, config)
        messages.listeners[threading.get_native_id()] = []
        while 1:
            data, method = messages.listen(threading.get_native_id())
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
