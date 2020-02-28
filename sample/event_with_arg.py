from .UdonPie import *  # IGNORE_LINE


def _onPlayerJoined(playerApi: VRCPlayerApi):
    Debug.Log(Object(playerApi))
