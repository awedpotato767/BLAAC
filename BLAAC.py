#!python3

import venv
import os
import tomllib
from random import choice
import logging
from src.tts import fancyTTSOutput, init_audio, terminate_audio

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


if __name__ == "__main__":
    init_audio()
    #initialise TTS outputs
    primary_TTS = fancyTTSOutput()
    secondary_TTS = fancyTTSOutput()
    secondary_TTS.say("welcome to B L A A C", volume=0.5)
    terminate_audio()
