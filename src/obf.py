import json as js
import os
import tomllib
import logging

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
with open("config/Global config.toml","rb") as conf_file:
    global_config = tomllib.load(conf_file)

class button:
    def __init__(self, button_dict):
        self.ID = str(button_dict["id"])
        self.label = button_dict["label"]
        self._data = button_dict

        self.loads_board = None
        if self.has_property("load_board"):
            if "path" in self._data["load_board"].keys():
                self.loads_board = self._data["load_board"]["path"]
            else:
                raise NotImplementedError
            #TODO support URLs

    def __repr__(self):
        retval = self.label
        if self.has_property("load_board"):
            retval += " *"
        return retval

    #check if a certain property is defined.
    def has_property(self, _property):
        return _property in self._data.keys()


    def vocalisation(self, voice = None):
        #TODO add custom voices
        if "vocalisation" in self._data.keys():
            return self._data["vocalisation"]
        return self.label



class board:
    def __init__(self, path_or_url):
        #TODO support URLs
        if path_or_url.startswith("http"):
            raise NotImplementedError
        with open(path_or_url) as fp:
            self._data = js.load(fp)

        self.buttons = {}
        for btn in self._data["buttons"]:
            self.buttons[str(btn["id"])] = button(btn)

        self.grid = []
        for row in range(self._data["grid"]["rows"]):
            self.grid.append([])
            for column in range(self._data["grid"]["columns"]):
                if self._data["grid"]["order"][row][column] != None:
                    self.grid[row].append(
                        self.buttons[str(self._data["grid"]["order"][row][column])])
                else:
                    self.grid[row].append(None)


    def __repr__(self):
        retval = ""
        colwidth = (160//len(self.grid[1]))
        for row in self.grid:
            retval += "\n"
            for btn in row:
                if btn == None:
                    btn = "_"
                retval += f'{repr(btn):<{colwidth}}'
        return retval



