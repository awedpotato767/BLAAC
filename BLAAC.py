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
    if f"{global_config["boards"]["home_board"]}.obf" not in os.listdir("Boards/"):
        boards_dir = f"Boards/{global_config["boards"]["home_board"]}/"
        #FIXME add error handling
        with open(boards_dir+"manifest.json") as mff:
            # obf.load_manifest(mff)
            pass
        AAC_board = obf.board("Boards/communikate-20/board_1_235.obf")

    inp = " "
    focused_btn = None
    focus_row = 0
    focus_column = 0
    focused_btn = AAC_board.grid[focus_row][focus_column]
    grid_width = len(AAC_board.grid[0])
    grid_height = len(AAC_board.grid)
    print("initialised")
    audio_feedback.say(f"This board is {grid_height} by {grid_width}. Focusing top left button {focused_btn.label}.", interrupt=False)
    sentence = ""
    while inp != "q":
        print(AAC_board)
        inp = str(input(":"))
        print(f'"{inp}"')
        if len(inp) == 2 and ord(inp[0])-ord("a")<15 and ord(inp[1])-ord("a")<15 :
            focus_row = ord(inp[0])-ord("a")
            focus_column = ord(inp[1])-ord("a")
            focused_btn = AAC_board.grid[focus_row][focus_column]
            if focused_btn.has_property("load_board"):
                audio_feedback.say(focused_btn.vocalisation()+ ": menu.")
            else:
                audio_feedback.say(focused_btn.vocalisation())
        elif inp == "s":
            if focused_btn.has_property("load_board"):
                audio_feedback.say("Entering board " + focused_btn.vocalisation())
                AAC_board = obf.board(boards_dir+ focused_btn.loads_board)
                focus_row = 0
                focus_column = 0
                focused_btn = AAC_board.grid[focus_row][focus_column]
                grid_width = len(AAC_board.grid[0])
                grid_height = len(AAC_board.grid)
                audio_feedback.say("focusing button "+focused_btn.label, interrupt=False)
            else:
                speech.say(focused_btn.vocalisation())
                sentence += focused_btn.vocalisation() + " "
                AAC_board = obf.board("Boards/communikate-20/board_1_235.obf")
        elif inp == "ss":
            speech.say(sentence.rstrip()+".")
            sentence = ""
        elif inp == "ds":
            sentence = ""
        elif inp == "":
            focus_column += 1
            if focus_column > grid_width:
                focus_row += 1
                focus_column = 1
            if focus_row > grid_height:
                focus_row = 1
            focused_btn = AAC_board.grid[focus_row][focus_column]

            if focused_btn.has_property("load_board"):
                audio_feedback.say(focused_btn.vocalisation()+ ": menu.")
            else:
                audio_feedback.say(focused_btn.vocalisation())
            print(focused_btn.label)
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
