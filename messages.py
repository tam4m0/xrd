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

import socket
import threading
from struct import unpack_from
from xmlrpc import client

from enums import *


class Messages:
    def getHandle(self):
        if self.handle == 0xFFFFFFFF:
            self.handle = 0x80000000
        elif self.handle == 0x80000000:
            pass
        else:
            self.handle += 1
        return self.handle

    def sendMessage(self, message):
        lenBytes = len(message).to_bytes(4, byteorder="little")
        handler = self.getHandle()
        handler_bytes = handler.to_bytes(4, byteorder="little")
        self.sock.sendall(lenBytes + handler_bytes + message)

    def whiteMessage(self, message, user, level, levelRequired):
        if user in self.whitelist.keys():
            if level.value >= levelRequired.value:
                self.sendMessage(message)
        else:
            pass

    def listen(self, whom):
        while 1:
            try:
                data, method = self.listeners[whom].pop(0)
                return data, method
            except IndexError as e:
                continue

    def recvWorker(self, sock):
        while 1:
            try:
                head = sock.recv(8)
                s, h = unpack_from("<LL", head)
                d, m = client.loads(sock.recv(s), use_builtin_types=True)
                if d == None:
                    pass
                else:
                    for l in self.listeners.keys():
                        self.listeners[l].append((d, m))
            except Exception as e:
                continue

    def __init__(self, sock, whitelist):
        self.handle = 0x80000000
        self.listeners = {}
        self.sock = sock
        self.whitelist = whitelist
        self.workThread = threading.Thread(target=self.recvWorker, args=(self.sock,))
        self.workThread.start()
