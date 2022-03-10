import ast
import importlib

import sectorum


class PluginsUtil:
    def __init__(self, config):
        self.config = config
        self.plugins = [
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
