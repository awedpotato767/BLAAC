#!python3

import venv
import os
import tomllib
from random import choice
import logging
from audioO import *
from keyboardI import *
from stateHandler import *
import obfIO as obf
import time

#start logger
logging.basicConfig(filename='logs/lastrun.log', encoding='utf-8', level=logging.DEBUG)
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
if os.path.isfile("config/config.toml"):
    with open("config/config.toml","rb") as conf_file:
        global_config = tomllib.load(conf_file)
else:
    with open("config/sample_config.toml","rb") as conf_file:
        global_config = tomllib.load(conf_file)
        conf_data = conf_file.read()
    with open("config/config.toml", "w") as cf:
        cf.write(str(conf_data))



if __name__ == "__main__":
    ##### Startup
    logger.info("BLAAC is starting up")
    ### initialise two audio channels
    speech_actor = audioOutput.start(\
        device_ID=global_config["startup"]["default_speaker"],\
        default_voice = global_config["tts"]["default_speaking_voice"]\
            )
    speech = speech_actor.proxy()

    #process any new voices then reload
    speech.preprocess_voice_dir(excluded_voices = speech.get_voices().get()).get()
    speech.load_voice_dir()

    audio_feedback_actor = audioOutput.start(\
        device_ID=global_config["startup"]["default_headphones"],\
        default_voice = global_config["tts"]["default_feedback_voice"],  \
        usually_interrupt=True\
            )
    audio_feedback = audio_feedback_actor.proxy()

    #Once the TTS is loaded, say a welcome message.
    #This serves the dual purpose of testing the AAC system for errors, and providing feedback to help non-visual users debug the program.

    logger.debug(audio_feedback.say(choice(global_config["startup"]["welcome_messages"])).get())


    ### load the home board on startup.
    # Since this parameter may be a name or a full path, we have to overspecify it somewhat.
    if global_config["boards"]["home_board"].startswith("http") or os.path.isfile(global_config["boards"]["home_board"]):
        AAC_board = board(global_config["boards"]["home_board"])

    elif os.path.isdir(f"Boards/{global_config["boards"]["home_board"]}/"):
        boards_dir = f"Boards/{global_config["boards"]["home_board"]}/"
        AAC_board, images, sounds = obf.load_obf_collection(boards_dir)

    elif os.path.isfile(f"Boards/{global_config["boards"]["home_board"]}.obf"):
        AAC_board = board(f"Boards/{global_config["boards"]["home_board"]}.obf")
    else:
        audio_feedback.say(f"Could not find home board {global_config["boards"]["home_board"]}. Aborting.").get()
        raise FileNotFoundError(f"Could not find home board {global_config["boards"]["home_board"]}. Aborting.")

    inp_actors = []
    out_actors = {"speech": speech_actor, "audio feedback": audio_feedback_actor, "multiline_text":None}
    state_handler_actor = stateHandler.start(inp_actors,out_actors, AAC_board)
    state_handler = state_handler_actor.proxy()

    keyboard_actor = keyboardInput.start(state_handler)

    state_handler.add_inp_actors([keyboard_actor])

    inp = " "
    focused_btn = None
    focus_row = 0
    focus_column = 0
    focused_btn = AAC_board.grid[focus_row][focus_column]
    grid_width = len(AAC_board.grid[0])
    grid_height = len(AAC_board.grid)


    audio_feedback.say(f"This board is {grid_height} by {grid_width}. Focusing top left button: {focused_btn.label}.", interrupt=False)
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

    logger.info("BLAAC is quitting")
    sd.wait()
    pykka.ActorRegistry.stop_all()
