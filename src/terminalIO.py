import pykka

import logging
import os
import tomllib

import sys
import curses
from configIO import global_config

#start logger
logger = logging.getLogger(__name__)


class keyboardInput(pykka.ThreadingActor):
    def __init__(self, state_handler):
        super().__init__()
        self._grid_size = (0,0)

    def on_start(self):
        #start input FSM
        x = 1



    def on_receive(self, message):
        match message:
            case {"grid_dimensions": (rows,columns)}:
                self._grid_size = (rows,columns)
            case _:
                print("unrecognised message")
        return "message handled"

