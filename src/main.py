#!python3

from pocket_tts import TTSModel, export_model_state
import scipy.io.wavfile
import os
import tomllib
import pyaudio
import logging
logger = logging.getLogger(__name__)

#config file reading
with open("../config/Global config.toml","rb") as conf_file:
    global_config = tomllib.load(conf_file)

#tts initialisation
tts_model = TTSModel.load_model(temp=0.6)
default_voice_filepath = f"../TTS voices/{global_config["startup"]["default_voice"]}.safetensors"
default_voice = tts_model.get_state_for_audio_prompt(default_voice_filepath)

 #voice initialisation
voices = {"default": default_voice}
voice_directory_files = os.listdir("../TTS voices")
precached_files = os.listdir("../TTS voices/cache")

#cache wav files for future runs
for filename in voice_directory_files:
    name, ext = os.path.splitext(filename)

    #warn for incorrect files
    if ext != ".safetensors" and ext != ".wav" and ext !="":
        logger.warning("could not load voice '" + name + "' - invalid file extension" + ext)

    #only cache files without a precached equivalent
    if ext==".wav" and f"{name}.safetensors" not in voice_directory_files\
                   and f"{name}.safetensors" not in precached_files:
        export_model_state(tts_model.get_state_for_audio_prompt("../TTS voices/"+filename),
                           "../TTS voices/cache/"+name+".safetensors")

#load cached files
for filename in os.listdir("../TTS voices/cache"):
    name,ext = os.path.splitext(filename)
    if ext==".safetensors":
        voices[name] = tts_model.get_state_for_audio_prompt("../TTS voices/cache/"+filename)
for filename in voice_directory_files:
    name,ext = os.path.splitext(filename)
    if ext==".safetensors":
        voices[name] = tts_model.get_state_for_audio_prompt("../TTS voices/"+filename)



#pyaudio initialisation
audio_dev = pyaudio.PyAudio()


def play_tts_audio(tts_model, voice_state, text):
    #open stream
    stream = audio_dev.open(format=pyaudio.paFloat32, channels=1, rate=24000, output=True)
    #generate audio
    for chunk in tts_model.generate_audio_stream(voice_state, text):
        chunk_bytes = bytes(chunk.numpy())
        stream.write(chunk_bytes)
    #leave
    stream.close()

#test code
play_tts_audio(tts_model, voices["default"], "Shall I compare thee to a summer's day? Thou art more fair and more temperate.")
play_tts_audio(tts_model, voices["neutral"], "Shall I compare thee to a summer's day? Thou art more fair and more temperate.")
play_tts_audio(tts_model, voices["chatty"], "Shall I compare thee to a summer's day? Thou art more fair and more temperate.")

play_tts_audio(tts_model, voices["everything is fine"], "Shall I compare thee to a summer's day? Thou art more fair and more temperate.")

