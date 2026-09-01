
from pocket_tts import TTSModel, export_model_state
import scipy.io.wavfile
import os
import tomllib
import pyaudio
import time
import logging
import torch.multiprocessing

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

#pyaudio setup
pyaudio_inst = None
def init_audio():
    #pyaudio initialisation
    global pyaudio_inst
    pyaudio_inst = pyaudio.PyAudio()
    return pyaudio_inst
def terminate_audio():
    pyaudio_inst.terminate()


#config file reading
with open("config/Global config.toml","rb") as conf_file:
    global_config = tomllib.load(conf_file)

#tts initialisation
__default_voice = None
__voices = {}

__tts_model = TTSModel.load_model(temp=0.6)

try:
    __default_voice =\
        __tts_model.get_state_for_audio_prompt(global_config["tts"]["default_voice"])
except ImportError:
    logger.warning(f"Default voice file '{global_config["tts"]["default_voice"]}' is not a WAV or safetensors file. Please make sure this file is present and correct. Continuing with generic voice 'alba'.")
    __default_voice =\
        __tts_model.get_state_for_audio_prompt("alba")


# needed for multiprocessing
def __buffer_TTS(text, voice, volume, output_queue):
            for chunk in __tts_model.generate_audio_stream(__voices[voice], text):
                output_queue.put(bytes((chunk*volume).numpy()))

#voice initialisation
def load_voices():
    voices = {"default": __default_voice}
    voice_directory_files = os.listdir("TTS voices")
    precached_files = os.listdir("TTS voices/cache")

    #cache voices from wav files for future runs
    for filename in voice_directory_files:
        name, ext = os.path.splitext(filename)

        #warn for incorrect files
        if ext != ".safetensors" and ext != ".wav" and ext !="":
            logger.warning("could not load voice '" + name + "' - invalid file extension" + ext)

        #only cache files without a precached equivalent
        if ext==".wav" and f"{name}.safetensors" not in voice_directory_files\
                    and f"{name}.safetensors" not in precached_files:
            export_model_state(__tts_model.get_state_for_audio_prompt("TTS voices/"+filename),
                            "TTS voices/cache/"+name+".safetensors")

    #load cached voices
    for filename in os.listdir("TTS voices/cache"):
        name,ext = os.path.splitext(filename)
        if ext==".safetensors":
            voices[name] = __tts_model.get_state_for_audio_prompt("TTS voices/cache/"+filename)
    #load precompiled voices in the TTS voices directory
    #These will take priority over equivalently named chache entries
    for filename in voice_directory_files:
        name,ext = os.path.splitext(filename)
        if ext==".safetensors":
            voices[name] = __tts_model.get_state_for_audio_prompt("TTS voices/"+filename)
    return voices

__voices = load_voices()



def get_voices():
    return __voices.keys()

def TTS_chunker(byte_count, audio_buffer):
    # might block forever
    bufa = audio_buffer.get()
    i = 0
    output = bytes()
    while True:
        if i+byte_count <= len(bufa):
            i += byte_count
            yield bufa[i-byte_count:i]
        else:
            if not audio_buffer.empty():
                output = bufa[i:]
                i = i+byte_count-len(bufa)
                bufa = audio_buffer.get()
                yield b''.join([output,bufa[:i]])
            else:
                break

#generate audio
def callback(in_data, frame_count, time_info, status):
    global TTS_chunks
    try:
        data = next(TTS_chunks)
    except StopIteration:
        data = bytes()
    return (data, pyaudio.paContinue)


def say(text, voice="default", volume=1):
    audio_buffer = torch.multiprocessing.Queue()


    TTS_generator = torch.multiprocessing.Process(target=__buffer_TTS, args=(text, voice, volume, audio_buffer))
    TTS_generator.start()
    global TTS_chunks
    TTS_chunks = TTS_chunker(52*4, audio_buffer)

    stream = pyaudio_inst.open(format=pyaudio.paFloat32, channels=1, rate=24000, stream_callback=callback, output=True)
    while stream.is_active():
        time.sleep(0.2)
    #stream will automatically close when generation has finished

