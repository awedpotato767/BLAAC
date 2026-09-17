import pykka

import logging
import os
import tomllib

#start logger
logger = logging.getLogger(__name__)

#check that this module is running in the root directory
#and check for the license text at the same time.
try:
    with open("README.md") as readme:
        if "This code is released under the CC BY-SA license." not in readme.read():
            raise EOFError("Cannot find license text in README.md")
except FileNotFoundError:
    raise FileNotFoundError("Cannot find README.md. Please run this code from the BLAAC root directory.")


#config file reading
if not os.path.isfile("config/config.toml"):
    with open("config/sample_config.toml","r") as conf_file:
        conf_data = conf_file.read()
    with open("config/config.toml", "w") as cf:
        cf.write(str(conf_data))

with open("config/config.toml","rb") as conf_file:
    global_config = tomllib.load(conf_file)


class keyboardInput(pykka.ThreadingActor):
    def __init__(self, state_handler):
        super().__init__()
        self._grid_size = (0,0)

    def on_start(self):
        pass



    def on_receive(self, message):
        match message:
            case {"grid_dimensions": (rows,columns)}:
                self._grid_size = (rows,columns)
            case _:
                print("unrecognised message")
        return "message handled"

