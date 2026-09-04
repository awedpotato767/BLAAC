#!python3

import venv
import os
import tomllib
from random import choice
import logging
from src.audioHandler import *

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
    #initialise both audio channels
    speech_handler = audioHandler.start(device_ID=global_config["startup"]["default_speaker"], temp=0.7)
    speech = speech_handler.proxy()

    audio_feedback_handler = audioHandler.start(device_ID=global_config["startup"]["default_speaker"], usually_interrupt=True)
    audio_feedback = audio_feedback_handler.proxy()

    #TODO if audio devices are the same, do this
    #    audio_feedback = speech


    audio_feedback.say(choice(global_config["startup"]["welcome_messages"]), voice="chatty")
    #audio prompts should have normalised volume
    speech.say("testing testing 123")



    time.sleep(10)
    #gracefully end the code
    sd.wait()
    pykka.ActorRegistry.stop_all()
