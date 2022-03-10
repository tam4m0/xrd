import ast
import importlib

# plugin tutorial:
#
# put plugins in ./plugins folder, add them to Makefile.spec, run make
#
# follow the rest of these comments and you'll be on your way
#
# import plugins here
import sectorum


class PluginsUtil:
    def __init__(self, config):
        self.config = config
        self.plugins = [
            # and set them to load automatically here
            "sectorum",
        ]

    def registerAllListeners(self, socket, messagesInstance):
        for pkg in self.plugins:
            exec(
                compile(
                    ast.parse(pkg + ".Main(socket, messagesInstance)"),
                    filename="",
                    mode="exec",
                )
            )
