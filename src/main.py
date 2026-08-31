#!python3

#temporary hardcoded values
default_voice = "../TTS voices/neutral.safetensors"

from pocket_tts import TTSModel
import scipy.io.wavfile
import os

import pyaudio
CHUNK = 1920

#tts initialisation
tts_model = TTSModel.load_model()
voice_state = tts_model.get_state_for_audio_prompt(default_voice)

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
play_tts_audio(tts_model, voice_state, "According to all known laws of aviation, there is no way a bee should be able to fly. Its wings are too small to get its fat little body off the ground. The bee, of course, flies anyway because bees don't care what humans think is impossible.")


audio_dev.terminate()
