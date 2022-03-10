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

from math import floor


class MessageGenerators:
    def splitCmd(data, method, typ):
        if typ == "CHAT":
            user = data[1]
            command = data[2].split(" ")[0]
            args = data[2][1:].split(" ")[1:]
            return (user, command, args)
        if typ == "CONN":
            login = data[0]
            spec = data[1]
            return (login, spec)
        if typ == "PEND":
            login = data[1]
            timescore = data[2]
            return (login, timescore)
        if typ == "PCHP":
            login = data[1]
            timescore = data[2]
            lap = data[3]
            cpindex = data[4]
            return (login, timescore, lap, cpindex)

    def timestrToHMS(timestr):
        s = int(timestr) / 1000
        m = s / 60
        s %= 60
        h = m / 60
        m %= 60
        return str(floor(h)) + "h" + str(floor(m)) + "m" + str(round(s, 2)) + "s"
