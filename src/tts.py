
from pocket_tts import TTSModel, export_model_state
import scipy.io.wavfile
import os
import tomllib
import pyaudio
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


class fancyTTSOutput:
    def __init__(self):
        self.__default_voice = None
        self.__voices = None


        #tts initialisation
        self.__tts_model = TTSModel.load_model(temp=0.6)

        try:
            self.__default_voice =\
                self.__tts_model.get_state_for_audio_prompt(global_config["tts"]["default_voice"])
        except ImportError:
            logger.warning(f"Default voice file '{global_config["tts"]["default_voice"]}' is not a WAV or safetensors file. Please make sure this file is present and correct. Continuing with generic voice 'alba'.")
            self.__default_voice =\
                self.__tts_model.get_state_for_audio_prompt("alba")


        #voice initialisation
        self.reload_voices()

    def reload_voices(self):
        self.__voices = {"default": self.__default_voice}
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
                export_model_state(tts_model.get_state_for_audio_prompt("TTS voices/"+filename),
                                "TTS voices/cache/"+name+".safetensors")

        #load cached voices
        for filename in os.listdir("TTS voices/cache"):
            name,ext = os.path.splitext(filename)
            if ext==".safetensors":
                self.__voices[name] = self.__tts_model.get_state_for_audio_prompt("TTS voices/cache/"+filename)
        #load precompiled voices in the TTS voices directory
        #These will take priority over equivalently named chache entries
        for filename in voice_directory_files:
            name,ext = os.path.splitext(filename)
            if ext==".safetensors":
                self.__voices[name] = self.__tts_model.get_state_for_audio_prompt("TTS voices/"+filename)

    def get_voices(self):
        return self.__voices.keys()

    def say(self, text, voice="default", volume=1):
        #open stream
        stream = pyaudio_inst.open(format=pyaudio.paFloat32, channels=1, rate=24000, output=True)
        #generate audio
        for chunk in self.__tts_model.generate_audio_stream(self.__voices[voice], text):
            chunk_bytes = bytes((chunk*volume).numpy())
            stream.write(chunk_bytes)

        #leave
        stream.close()

if __name__ == "__main__":
    test_speaker = fancyTTSOutput()
     #test code
    test_speaker.say("Shall I compare thee to a summer's day? Thou art more fair and more temperate.", volume=5)
    test_speaker.say("Shall I compare thee to a summer's day? Thou art more fair and more temperate.", "neutral")
    test_speaker.say("Shall I compare thee to a summer's day? Thou art more fair and more temperate.", "chatty")
    test_speaker.say("Shall I compare thee to a summer's day? Thou art more fair and more temperate.", "everything is fine")
