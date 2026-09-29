import json as js
import os
import tomllib
import logging
import urllib

from configIO import global_config

#start logger
logger = logging.getLogger(__name__)


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
        match path_or_url:
            case "http*":
                #download the file
                with urllib.request.urlopen(path_or_url) as fp:
                    self._data = js.load(fp)
                    contents = fp.read()
                #save a local copy
                with open(f"{self._boardroot}cache/{self._data["id"]}.obf", "w") as obffile:
                    obffile.write(contents)
            case _:
                #assume it is a file.
                #This code will raise hell if it isn't, but that should be caught downstream by whichever numpty has made this mistake.
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
                btn_rep = repr(btn)
                if btn == None:
                    btn_rep = ""
                retval += f'{btn_rep:<{colwidth}}'
        return retval

def load_obf_collection(directory):
    if not directory.endswith("/"):
        directory += "/"

    ### find the manifest
    try:
        with open(directory+"manifest.json","r") as mf:
            mf_data = js.load(mf)
    except FileNotFoundError as e:
        logger.warning(f"Could not load board: {e}")
        return None, None, None

    assert mf_data["format"] == "open-board-0.1"

    ### load sound and images
    images = {}
    sounds = {}

    ### decode the root board
    root_board = board(directory+mf_data["root"])

    ###
    return root_board, images, sounds


