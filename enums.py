from enum import Enum

PowerLevels = Enum(
    value="PowerLevels", names=[("MasterAdmin", 9), ("Operator", 8), ("Moderator", 7)]
)
