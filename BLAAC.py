#!python3

import venv
import os
import tomllib
from random import choice
import logging
from src.audioHandler import *
import src.obf as obf

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
    speech_handler = audioHandler.start(device_ID=global_config["startup"]["default_speaker"], temp=0.7, voice = global_config["tts"]["default_speaking_voice"])
    speech = speech_handler.proxy()

    audio_feedback_handler = audioHandler.start(device_ID=global_config["startup"]["default_headphones"], voice = global_config["tts"]["default_feedback_voice"], usually_interrupt=True)
    audio_feedback = audio_feedback_handler.proxy()

    #TODO if audio devices are the same, do this
    #    audio_feedback = speech


    print(audio_feedback.say(choice(global_config["startup"]["welcome_messages"]), voice="chatty").get())

    #test code
    AAC_board = obf.board("Boards/communikate-20/board_1_235.obf")
    boards_dir = "Boards/communikate-20/"

    inp = " "
    while inp != "":
        print(AAC_board)
        inp = str(input(":"))

        if len(inp) == 2 and inp.isnumeric():
            selected_btn = AAC_board.grid[int(inp[1])-1][int(inp[0])-1]
            if selected_btn.has_property("load_board"):
                audio_feedback.say(selected_btn.vocalisation())
                AAC_board = obf.board(boards_dir+ selected_btn.loads_board)
            else:
                speech.say(selected_btn.vocalisation())
        elif inp in speech.get_voices().get():
            speech.current_voice = inp
            audio_feedback.say("selected voice "+inp)
        elif inp == "v":
            _voices = ""
            for voice in speech.get_voices().get()[:-1]:
                _voices = _voices + f"{voice}, "
            _voices += f"and {speech.get_voices().get()[-1]}"
            audio_feedback.say(f"the available voices are: {_voices}.")
        elif inp.startswith("s "):
            speech.say(inp.removeprefix("s "))
        else:
            audio_feedback.say("Not a command.")
    #gracefully end the code
    sd.wait()
    pykka.ActorRegistry.stop_all()
