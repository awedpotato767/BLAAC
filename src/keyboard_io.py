import logging
import os
import tomllib

import pykka

# start logger
logger = logging.getLogger(__name__)

# check that this module is running in the root directory
# and check for the license text at the same time.

class KeyboardInput(pykka.ThreadingActor):
    def __init__(self, state_handler):
        super().__init__()
        self._grid_size = (0, 0)

    def on_start(self):
        pass

    def on_receive(self, message):
        match message:
            case {"grid_dimensions": (rows, columns)}:
                self._grid_size = (rows, columns)
            case _:
                print("unrecognised message")
        return "message handled"
