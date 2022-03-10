import ast
import importlib

# plugin tutorial:
#
# put plugins in ./plugins folder, add them to Makefile.spec, run make
#
# follow the rest of these comments and you'll be on your way
#
# import plugins here and set the same thing in conf.ini
import sectorum


class PluginsUtil:
    def __init__(self, config):
        self.config = config
        self.plugins = [x for x in self.config["Plugins"]["list"].split(":")]

    def registerAllListeners(self, socket, messagesInstance):
        for pkg in self.plugins:
            exec(
                compile(
                    ast.parse(pkg + ".Main(socket, messagesInstance)"),
                    filename="",
                    mode="exec",
                )
            )
