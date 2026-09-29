#!python3

# generic python modules
import venv
import os
from random import choice
import logging
import time
from configIO import global_config

# import devices
from stateHandler import *
from terminalIO import *
from audioO import *
import obfIO as obf


#start logger
logging.basicConfig(filename='logs/lastrun.log', encoding='utf-8', level=logging.DEBUG)
logger = logging.getLogger(__name__)



if __name__ == "__main__":
    ##### Startup
    logger.info("BLAAC is starting up")

    ### actor setup

    inp_actors = []
    out_actors = {"speech": None, "audio feedback": None, "multiline_text":None}

    #if terminal mode is being used, initialise the keyboard input and suitable text outputs:
    if global_config["devices"]["terminal"] == True:
        pass
        #TODO figure out how to get text output and input working nicely.


    #if an audio device is enabled, initialise two audio channels
    if global_config["devices"]["speaker"] or global_config["devices"]["headphones"]:
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


    #once the board and IO actors have started, start BLAAC proper.
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

    #gracefully end the code

    logger.info("BLAAC is quitting")
    sd.wait()
    pykka.ActorRegistry.stop_all()
