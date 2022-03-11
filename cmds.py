# This file is part of xrd.
#
# xrd is free software: you can redistribute it and/or modify it under the terms of
# the GNU General Public License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.
#
# xrd is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with xrd.
# If not, see <https://www.gnu.org/licenses/>.

import ast
import os
import pathlib
import socket
import subprocess
import threading
from inspect import getdoc

import sectorum

from enums import *
from messagegen import *
from messages import *


class Commands:
    def __init__(self, sock, messages, config):
        self.sock = sock
        self.config = config
        self.messages = messages
        self.messages.listeners[threading.get_native_id()] = []

    def xhelp(self, user, cmd, args):
        docs = [
            [
                " /echo:",
                getdoc(self.echo),
                " /hacktheplanet:",
                getdoc(self.hacktheplanet),
                " /ban:",
                getdoc(self.ban),
                " /unban:",
                getdoc(self.unban),
                " /kick:",
                getdoc(self.kick),
                " For the next page of help, use /help 2.",
            ],
            [
                " /mute:",
                getdoc(self.mute),
                " /unmute:",
                getdoc(self.unmute),
                " /forceskip:",
                getdoc(self.forceskip),
                " /forcerestart:",
                getdoc(self.forcerestart),
                " /delchall:",
                getdoc(self.delchall),
                " For the next page of help, use /help 3.",
            ],
            [
                " /updchalls:",
                getdoc(self.updchalls),
                " /getchalls:",
                getdoc(self.getchalls),
                " /updplugins:",
                getdoc(self.updplugins),
            ],
        ]
        try:
            if int(args[0]) == 0:
                args[0] = 1
            for ds in docs[int(args[0]) - 1]:
                self.messages.sendMessage(
                    client.dumps((ds, user), methodname="ChatSendToLogin").encode()
                )
        except IndexError as e:
            args = [1]
            self.xhelp(user, cmd, args)

    def echo(self, user, cmd, args):
        """Echoes whatever you put in, but only to you."""
        self.messages.sendMessage(
            client.dumps((" ".join(args), user), methodname="ChatSendToLogin").encode()
        )

    def hacktheplanet(self, user, cmd, args):
        """Free Kevin!"""
        self.messages.sendMessage(
            client.dumps(
                (user, "You've been arrested by the CIA for hacking, GG."),
                methodname="Kick",
            ).encode()
        )

    def ban(self, user, cmd, args):
        """Bans the user specified. Only available to Operator and above."""
        self.messages.whiteMessage(
            client.dumps(
                (args[0], "The ban hammer has spoken!", True),
                methodname="BanAndBlackList",
            ).encode(),
            user,
            MessageGenerators.getLevel(self.config["WhiteList"][user]),
            MessageGenerators.getLevel("Operator"),
        )

    def unban(self, user, cmd, args):
        """Unbans the user specified. Only available to Operator and above."""
        self.messages.whiteMessage(
            client.dumps((args[0],), methodname="UnBan").encode(),
            user,
            PowerLevels[self.config["WhiteList"][user]],
            PowerLevels.Operator,
        )
        self.messages.whiteMessage(
            client.dumps((args[0],), methodname="UnBlackList").encode(),
            user,
            PowerLevels[self.config["WhiteList"][user]],
            PowerLevels.Operator,
        )

    def kick(self, user, cmd, args):
        """Kicks the user specified. Only available to Moderator and above."""
        self.messages.whiteMessage(
            client.dumps(
                (args[0], "You've been booted, get out!"), methodname="Kick"
            ).encode(),
            user,
            PowerLevels[self.config["WhiteList"][user]],
            PowerLevels.Moderator,
        )

    def mute(self, user, cmd, args):
        """Mutes the user specified. Only available to Moderator and above."""
        self.messages.whiteMessage(
            client.dumps((args[0],), methodname="Ignore").encode(),
            user,
            PowerLevels[self.config["WhiteList"][user]],
            PowerLevels.Moderator,
        )

    def unmute(self, user, cmd, args):
        """Unmutes the user specified. Only available to Moderator and above."""
        self.messages.whiteMessage(
            client.dumps((args[0],), methodname="UnIgnore").encode(),
            user,
            PowerLevels[self.config["WhiteList"][user]],
            PowerLevels.Moderator,
        )

    def forceskip(self, user, cmd, args):
        """Forces a skip to the next Challenge. Only available to Moderator and above."""
        self.messages.whiteMessage(
            client.dumps(tuple(), methodname="NextChallenge").encode(),
            user,
            PowerLevels[self.config["WhiteList"][user]],
            PowerLevels.Moderator,
        )

    def forcerestart(self, user, cmd, args):
        """Forces a restart of the current Challenge. Only available to Moderator and above."""
        self.messages.whiteMessage(
            client.dumps(tuple(), methodname="RestartChallenge").encode(),
            user,
            PowerLevels[self.config["WhiteList"][user]],
            PowerLevels.Moderator,
        )

    def delchall(self, user, cmd, args):
        """Deletes a specified Challenge. Only available to Operator and above. Hint: Use /getchalls to get every Challenge name."""
        self.messages.whiteMessage(
            client.dumps((args[0],), methodname="RemoveChallenge").encode(),
            user,
            PowerLevels[self.config["WhiteList"][user]],
            PowerLevels.Operator,
        )

    def updchalls(self, user, cmd, args):
        """Add all challenges not currently in the tracksfolder. It must be defined for this to work. Only available to Operator and above."""
        if user in self.config["WhiteList"].keys():
            if (
                PowerLevels[self.config["WhiteList"][user]].value
                >= PowerLevels.Operator.value
            ):
                if os.path.exists(self.config["Main"]["tracksfolder"]):
                    for r, d, f in os.walk(self.config["Main"]["tracksfolder"]):
                        for n in f:
                            print("DEBUG [tr]:", n)

    def getchalls(self, user, cmd, args):
        """Gets all challenge names in the tracksfolder."""
        if os.path.exists(self.config["Main"]["tracksfolder"]):
            for r, d, f in os.walk(self.config["Main"]["tracksfolder"]):
                for n in f:
                    self.messages.sendMessage(
                        client.dumps((n,), methodname="ChatSendToLogin").encode()
                    )

    def updplugins(self, user, cmd, args):
        """Updates all plugins in the plugins directory, rebuilding the program and halting it. Only available to MasterAdmin and above."""
        if user in self.config["WhiteList"].keys():
            if (
                PowerLevels[self.config["WhiteList"][user]].value
                >= PowerLevels.MasterAdmin.value
            ):
                os.chdir(self.config["Plugins"]["workdir"])
                p = subprocess.Popen(("make"))
                p.wait()
                print("INFO [mc]: Rebuild completed, halting server...")
                os._exit(0)
