
from pocket_tts import TTSModel, export_model_state
import scipy.io.wavfile
import os
import tomllib
import logging
import pykka

import sounddevice as sd
from torchaudio import transforms
import numpy
import time

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

#                                                             #
# Actor for TTS generation and wav file output to one device  #
#                                                             #

# Attributes

# _TTS_model -> an instance of TTSModel from pocketTTS.
#             -> Very bulky object. Don't pass around.
#
# _voices    -> dict() with keys labelling different voices loaded
#                 into the model (acts as a cache).
#             -> values are model states corresponding to each voice

# functions

# Init:
#
#  actions:
#    Creates a new instance of pocket-tts' 100k parameter model
#    Creates _voices
#    Adds a "default" entry to _voices.
#
#  parameters:
#       Specific to pocket-tts and sounddevice.
#
#    device_ID: int or str
#     - numerical ID of audio output device, or substring of device name
#     - see sounddevice documentation for more details
#    voice: string or string file path to a .safetensors
#     - name or filepath of voice to initialise the TTS with.
#     - Setting this value to a WAV file will slow down starting each actor
#    model: String
#     - which language model to use. highly recommended not to change this.
#    temp: strictly positive float
#     - values over 1 are not recommended.
#     - determines how random the model will be with its expressions
#    quant: bool
#     - setting this value to True decreases the audio quality
#         but marginally improves performance on some devices
#
#  errors:
#    TODO add more suitable error handling. Currently liable to raise ImportError a lot.

# load_voice_dir:
#
#  actions:
#    attempts to cache all .safetensors voices from the given directory into _voices.
#
#  parameters:
#    dirpath: str
#      - path to directory to search. Will be relative to the CWD, which should be the project root.

# preprocess_voice_dir:
#
#  actions:
#   Processes all "X.wav"-style files into a corresponding "cache/X.safetensors" file
#    unless X is present in _voices
#   NOTE: to reload all chache, simply run this file with an empty _voices dictionary
#   NOTE 2: For performance reasons, it is advisble to load all voices in dirpath, preprocess, then load again.
#
#  parameters:
#   see load_voice_dir()



class audioHandler(pykka.ThreadingActor):
    def __init__(self,
                 device_ID=None,
                 voice=global_config["tts"]["default_voice"],
                 model=None, temp=0.5, quant=False):
        #initialise actor code
        super().__init__()

        #load TTS
        self._TTS_model = TTSModel.load_model(language=model, temp=temp, quantize=quant)
        self._voices = {}
        #ensure voices dict is nonempty.
        # TODO gracefully continue on ImportError with suitable warning using default voice "charles"
        self._voices["default"] = self._TTS_model.get_state_for_audio_prompt(voice)

        #initialise audio stream TODO
        self.output_device = device_ID
        self.output_channels = 2
        self._TTS_sample_rate = 24000
        self._output_sample_rate = 48000
        #set transform for upsampling
        self._transform = transforms.Resample(self._TTS_sample_rate, self._output_sample_rate)

    def load_voice_dir(self, dirpath="TTS voices"):
        for fname in os.listdir(path):
            name, ext = os.splitext(fname)
            # Reload any voices found, except default.
            if ext == ".safetensors" and name != "default":
                self._voices=\
                    self._TTS_model.get_state_for_audio_prompt(fname)

    def preprocess_voice_dir(self, dirpath="TTS voices"):
        for fname in os.listdir(path):
            name, ext = os.splitext(fname)
            # preprocesses every wav file that has not been loaded yet.
            if ext == ".wav" and name not in self._voices.keys():
                export_model_state(self._TTS_model.get_state_for_audio_prompt(fname),
                                   dirpath.rstirp("/")+"/cache/"+name+".safetensors")


    def say(self, text, voice="default", volume=1.00):
        #temporary shit version
        audio_generator = self._TTS_model.generate_audio_stream(self._voices[voice], text)



        current_frame = 0
        finished=False
        def set_finished():
            nonlocal finished
            finished = True

        buf = self._transform(next(audio_generator)*volume).numpy()
        if self.output_channels == 2:
            buf = numpy.stack((buf,buf),axis=1)
        def callback(outdata, frames, time, status):
            nonlocal current_frame
            nonlocal buf
            if status:
                print(status)
            chunksize = min(len(buf) - current_frame, frames)
            outdata[:chunksize] = buf[current_frame:current_frame + chunksize]
            if chunksize < frames:
                try:
                    buf = self._transform(next(audio_generator)*volume).numpy()
                    if self.output_channels == 2:
                        buf = numpy.stack((buf,buf),axis=1)
                    outdata[chunksize:] = buf[:frames-chunksize]
                    current_frame = frames-2*chunksize
                except StopIteration:
                    outdata[chunksize:] = 0
                    raise sd.CallbackStop()
            current_frame += chunksize
        stream = sd.OutputStream(samplerate= self._output_sample_rate, device=self.output_device, channels=self.output_channels, callback=callback, finished_callback=set_finished)
        with stream:
            while not finished:
                time.sleep(0.1)
        return "finished playing"


if __name__ == "__main__":
    speech_handler = audioHandler.start(device_ID="Ryzen")
    speech_proxy = speech_handler.proxy()

    audio_feedback_handler = audioHandler.start()
    audio_feedback_proxy = audio_feedback_handler.proxy()

    input("start")
    speech_proxy.say("This is speech"))
    audio_feedback_proxy.say("This is audio feedback")
    input("next input")


    sd.wait()
    pykka.ActorRegistry.stop_all()
