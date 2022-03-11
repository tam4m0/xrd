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

import configparser
import os

config = configparser.ConfigParser()
config.read("conf.ini")
config["Plugins"]["workdir"] = os.getcwd()
with open("conf.ini", "w") as f:
    config.write(f)
