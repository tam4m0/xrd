import ast
import importlib
import threading

# plugin tutorial:
#
# put plugins in ./plugins folder, add them to Makefile.spec, run make
#
# import plugins here and set the same thing in conf.ini
import sectorum


class PluginsUtil:
    def __init__(self, config):
        self.config = config
        self.plugins = [x for x in self.config["Plugins"]["list"].split(":")]

    def registerAllListeners(self, socket, messagesInstance):
        for pkg in self.plugins:
            t = threading.Thread(
                target=self.spinOffThreadToInstance,
                args=(pkg, socket, messagesInstance),
            )
            t.start()

    def spinOffThreadToInstance(self, pkgname, socket, messagesInstance):
        exec(
            compile(
                ast.parse(pkgname + ".Main(socket, messagesInstance, self.config)"),
                filename="",
                mode="exec",
            )
        )
