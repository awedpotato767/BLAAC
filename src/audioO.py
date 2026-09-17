
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
if not os.path.isfile("config/config.toml"):
    with open("config/sample_config.toml","r") as conf_file:
        conf_data = conf_file.read()
    with open("config/config.toml", "w") as cf:
        cf.write(str(conf_data))

with open("config/config.toml","rb") as conf_file:
    global_config = tomllib.load(conf_file)

#                                                             #
# Actor for TTS generation and wav file output to one device  #
#                                                             #

# Attributes

# _TTS_model -> an instance of TTSModel from pocketTTS.
#             -> Very bulky object. Don't pass around.
#
# _TTS_sample_rate -> the sample rate of any generated audio
#
# _voices    -> dict() with keys labelling different voices loaded
#                 into the model (acts as a cache).
#             -> values are model states corresponding to each voice
#
# current_voice -> the voice that this actor will say TTS things with
#
#
#
# Methods:
# __init__
# load_voice_dir()
# preprocess_voice_dir()
# get_voices()
# say()


class audioOutput(pykka.ThreadingActor):

# __init__: THIS IS A TIME EXPENSIVE OPERATION AND A MEMORY EXPENSIVE CLASS
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


    def __init__(self,
                 device_ID=None,
                 default_voice=global_config["tts"]["default_speaking_voice"],
                 model=None, temp=0.3, quant=False, usually_interrupt=False):
        super().__init__()
        #take in parameters for use in on_start()
        self._model = model
        self._quant = quant
        self._temp = temp
        self._default_voice = default_voice


        ### initialise audio device
        #TODO add proper error handling, support mono devices
        self.output_device = device_ID
        self.output_channels = 2
        #FIXME might crash if no audio device connected
        try:
            self._output_sample_rate = sd.query_devices(device = self.output_device)["default_samplerate"]
        except ValueError as e:
            logger.error(e)
            logger.error("invalid device "+ self.output_device+ ", using default.")
            self.output_device = sd.default.device[1]
            self._output_sample_rate = sd.query_devices(device = self.output_device)["default_samplerate"]
        self._stream = None
        self._interrupt = False
        self.usually_interrupt = usually_interrupt
        self.volume = 1.000


    def on_start(self):
        # where the heavy stuff goes to speed up the main thread.
        ### load TTS from pocket TTS

        self._TTS_model = TTSModel.load_model(language = self._model, temp=float(self._temp), quantize=self._quant, eos_threshold=-4.0)

        self._TTS_sample_rate = 24000


        ### set up a dictionary for available voices for this TTS
        #set up variable
        self._voices = {}

        #ensure voices dict is nonempty by adding a "default" entry.
        try:
            self._voices["default"] = self._TTS_model.get_state_for_audio_prompt(self._default_voice)
        except FileNotFoundError:
            logger.warning(f"Cannot find voice file '{self._default_voice}', continuing with prepackaged voice charles." )
            self._voices["default"] = self._TTS_model.get_state_for_audio_prompt("charles")
        #FIXME get it to throw an ImportError and figure out how to handle that.


        #use the default entry
        self.current_voice = "default"
        #load any saved voices
        self.load_voice_dir()

        #set transform for upsampling
        self._transform = transforms.Resample(self._TTS_sample_rate, self._output_sample_rate)

    def on_failure(self, exception_type, exception_value, traceback):
        logger.critical(exception_type + exception_value)



# load_voice_dir: AVERAGE VOICE SIZE IS 10-20MB. 100 voices -> >1GB. BE MINDFUL OF UNUSED VOICES
#
#  actions:
#    attempts to cache all .safetensors voices from the given directory into _voices.
#
#  parameters:
#    dirpath: str
#      - path to directory to search. Will be relative to the CWD, which should be the project root.


    def load_voice_dir(self, dirpath="TTS voices/"):
        for fname in os.listdir(dirpath):
            name, ext = os.path.splitext(fname.lower())
            # Reload any voices found, except default.
            if ext == ".safetensors" and name != "default":
                self._voices[name]=\
                    self._TTS_model.get_state_for_audio_prompt(dirpath+fname)
        if not dirpath.endswith("cache/") and os.path.isdir(dirpath+"cache/"):
            self.load_voice_dir(dirpath+"cache/")

# preprocess_voice_dir: THIS IS A TIME EXPENSIVE OPERATION.
#
#  actions:
#   Processes all "X.wav"-style files into a corresponding "cache/X.safetensors" file
#    unless X is present in _voices
#   NOTE: to reload all chache, simply run this file with an empty _voices dictionary
#   NOTE 2: For performance reasons, it is advisble to load all voices in dirpath, preprocess, then load again.
#
#  parameters:
#   dirpath -> directory containing all files to load
#   excluded_voices -> a list of strings (such as "default", "chatty", "news") containing voies to avoid loading.



    def preprocess_voice_dir(self, dirpath="TTS voices/", excluded_voices=[]):
        logger.info("preproccessing voices in "+dirpath)
        for fname in os.listdir(dirpath):
            name, ext = os.path.splitext(fname.lower())
            # preprocesses every wav file that has not been loaded yet.
            if ext == ".wav" and name not in excluded_voices:
                logger.info("preprocessing "+fname.lower())
                export_model_state(self._TTS_model.get_state_for_audio_prompt(dirpath+fname),
                                   dirpath+"cache/"+name+".safetensors")
        logger.info("preproccessing done")
# get_voices:
# a little helper function that retrieves a user friendly list for all
# acceptable values of "current_voice"

    def get_voices(self):
        return list(self._voices.keys())

# say:
#
#  actions:
#   Generates TTS speech from the given text, and sends it to a given audio device.
#
#  parameters:
#   text - what to say
#   volume --> how to say it
#   voice  -^
#   interrupt - interrupt the previous speech output. NB cannot interrupt two outputs back at present.
    def say(self, text, voice=None, volume=None, interrupt=None):
        #use class defaults for unspecified parameters
        if voice is None:
            voice = self.current_voice
        if interrupt is None:
            interrupt = self.usually_interrupt
        if volume is None:
            volume = self.volume

        #preprocess text to ensure it works
        text = text.lstrip(" ")
        #hotfix for short words
        padding = 5
        if len(text) < 7:
            padding = 8

        try:
            voice_state = self._voices[voice]
        except KeyError:
            voice_state = self._TTS_model.get_state_for_audio_prompt(voice)
            self._voices[voice] = voice_state
        audio_generator = self._TTS_model.generate_audio_stream(voice_state, text, frames_after_eos=padding)

        current_frame = 0
        finished=False
        def set_finished():
            nonlocal finished
            self._stream = None
            finished = True

        bufa = self._transform(next(audio_generator)*volume).numpy()
        if self.output_channels == 2:
            bufa = numpy.stack((bufa,bufa),axis=1)
        bufb = None
        def callback(outdata, frames, time, status):
            nonlocal current_frame
            nonlocal bufa
            nonlocal bufb
            if status:
                print(status)
            chunksize = min(len(bufa) - current_frame, frames)
            if current_frame<=frames:
                try:
                    bufb = self._transform(next(audio_generator)*volume).numpy()
                    if self.output_channels == 2:
                        bufb = numpy.stack((bufb,bufb),axis=1)
                except StopIteration:
                    outdata[chunksize:] = 0
                    raise sd.CallbackStop()
            outdata[:chunksize] = bufa[current_frame:current_frame + chunksize]
            if chunksize < frames:
                bufa = bufb.copy()
                outdata[chunksize:] = bufa[:frames-chunksize]
                current_frame = frames-2*chunksize


            if self._interrupt:
                outdata.fill(0)
                raise sd.CallbackStop()
            current_frame += chunksize

        #interrupt previous audio
        self._interrupt=interrupt
        while self._stream != None:
            time.sleep(0.1)
        self._interrupt = False
        try:
            self._stream = sd.OutputStream(samplerate= self._output_sample_rate, device=self.output_device, channels=self.output_channels, callback=callback, finished_callback=set_finished)
            self._stream.start()
        except Exception as e:
            logger.error(f"could not say {text} on {self.output_device}: {e}\n")
            return "could not start playing audio"
        return "started playing"

    def play(audio, volume = None, interrupt = None):
        raise NotImplementedError
