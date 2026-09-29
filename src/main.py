#!python3

import logging
import os
from random import choice

import pykka
import sounddevice as sd
import src.obf_io as obf
from src.audio_io import AudioOutput
from src.config import Config, ConfigFile, DeviceInfo, CONFIG_FOLDER
from src.keyboard_io import KeyboardInput
from src.obf_io import Board
from src.state_handler import StateHandler

# start logger
try:
    logging.basicConfig(filename="logs/lastrun.log", encoding="utf-8", level=logging.DEBUG)
except:
    print("ok")
logger = logging.getLogger(__name__)

def choose_device(chosen: DeviceInfo | None = None) -> DeviceInfo | None:
    """Creates a terminal menu of all output devices.
    On selection fail the currently selected device is chosen.
    If no device is selected the os default device is chosen.
    If there is no default device returns None (this should be changed)
    """
    output_devices = DeviceInfo.get_output_devices()

    default_out = DeviceInfo.get_default_output_device()

    for i, device in enumerate(output_devices):
        marker = "*" if chosen and device == chosen else " "
        default_indicator = "--> (default out)" if device == default_out else ""
        print(f"{marker} {i}: {device.name} {default_indicator}")

    try:
        selection = int(input(": "))
        return output_devices[selection]
    except (ValueError, TypeError, LookupError):
        return chosen if chosen else default_out


def init_config() -> Config:
    """Loads initial configuration of programme from file.
    If no file is present or fields missing, it prompts the user for values"""
    if not CONFIG_FOLDER.exists():
        os.mkdir(CONFIG_FOLDER)

    loaded_config = ConfigFile.load()

    speaker = (
        DeviceInfo.from_device_name(loaded_config.default_speaker)
        if loaded_config.default_speaker
        else choose_device()
    )
    headphones = (
        DeviceInfo.from_device_name(loaded_config.default_headphones)
        if loaded_config.default_headphones
        else choose_device()
    )

    config = Config.model_validate(
        {
            **loaded_config.model_dump(),
            "default_speaker": speaker,
            "default_headphones": headphones,
        }
    )

    config.into_config_file().save()
    return config


def main() -> None:
    """Entry point of programme"""
    ##### Startup
    logger.info("BLAAC is starting up")
    config = init_config()

    ### initialise two audio channels
    speech_actor = AudioOutput.start(
        device_ID=config.default_speaker.name, default_voice=config.default_speaking_voice
    )
    speech = speech_actor.proxy()

    # process any new voices then reload
    speech.preprocess_voice_dir(excluded_voices=speech.get_voices().get()).get()
    speech.load_voice_dir()

    audio_feedback_actor = AudioOutput.start(
        device_ID=config.default_headphones.name,
        default_voice=config.default_speaking_voice,
        usually_interrupt=True,
    )
    audio_feedback = audio_feedback_actor.proxy()

    # Once the TTS is loaded, say a welcome message.
    # This serves the dual purpose of testing the AAC system for errors, and providing feedback to help non-visual users debug the program.

    logger.debug(audio_feedback.say(choice(config.welcome_messages)).get())

    ### load the home board on startup.
    # Since this parameter may be a name or a full path, we have to overspecify it somewhat.

    print(config.home_board,os.path.isfile(config.home_board) )
    if str(config.home_board).startswith("http") or os.path.isfile(config.home_board):
        AAC_board = Board(config.home_board)  # this may be unbound!!

    elif os.path.isdir(config.home_board):
        AAC_board, images, sounds = obf.load_obf_collection(str(config.home_board))

    elif os.path.isfile(f"boards/{config.home_board}.obf"):
        AAC_board = Board(f"boards/{config.home_board}.obf")
    else:
        audio_feedback.say(
            f"Could not find home board {config.home_board}. Aborting."
        ).get()
        raise FileNotFoundError(
            f"Could not find home board {config.home_board}. Aborting."
        )

    inp_actors = []
    out_actors = {
        "speech": speech_actor,
        "audio feedback": audio_feedback_actor,
        "multiline_text": None,
    }
    state_handler_actor = StateHandler.start(inp_actors, out_actors, AAC_board)
    state_handler = state_handler_actor.proxy()

    keyboard_actor = KeyboardInput.start(state_handler)

    state_handler.add_inp_actors([keyboard_actor])

    inp = " "
    focused_btn = None
    focus_row = 0
    focus_column = 0
    focused_btn = AAC_board.grid[focus_row][focus_column]
    grid_width = len(AAC_board.grid[0])
    grid_height = len(AAC_board.grid)

    audio_feedback.say(
        f"This board is {grid_height} by {grid_width}. Focusing top left button: {focused_btn.label}.",
        interrupt=False,
    )
    sentence = ""

    while inp != "q":
        print(AAC_board)
        inp = str(input(":"))
        print(f'"{inp}"')
        if (
            len(inp) == 2
            and ord(inp[0]) - ord("a") < 15
            and ord(inp[1]) - ord("a") < 15
        ):
            focus_row = ord(inp[0]) - ord("a")
            focus_column = ord(inp[1]) - ord("a")
            focused_btn = AAC_board.grid[focus_row][focus_column]
            if focused_btn.has_property("load_board"):
                audio_feedback.say(focused_btn.vocalisation() + ": menu.")
            else:
                audio_feedback.say(focused_btn.vocalisation())
        elif inp == "s":
            if focused_btn.has_property("load_board"):
                audio_feedback.say("Entering board " + focused_btn.vocalisation())
                AAC_board = Board(
                    boards_dir + focused_btn.loads_board
                )  # boards_dir may be unbound!!
                focus_row = 0
                focus_column = 0
                focused_btn = AAC_board.grid[focus_row][focus_column]
                grid_width = len(AAC_board.grid[0])
                grid_height = len(AAC_board.grid)
                audio_feedback.say(
                    "focusing button " + focused_btn.label, interrupt=False
                )
            else:
                speech.say(focused_btn.vocalisation())
                sentence += focused_btn.vocalisation() + " "
                AAC_board = Board("boards/communikate-20/board_1_235.obf")
        elif inp == "ss":
            speech.say(sentence.rstrip() + ".")
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
                audio_feedback.say(focused_btn.vocalisation() + ": menu.")
            else:
                audio_feedback.say(focused_btn.vocalisation())
            print(focused_btn.label)
        elif inp in speech.get_voices().get():
            speech.current_voice = inp
            audio_feedback.say("selected voice " + inp)
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
    # gracefully end the code

    logger.info("BLAAC is quitting")
    sd.wait()
    pykka.ActorRegistry.stop_all()


if __name__ == "__main__":
    main()
