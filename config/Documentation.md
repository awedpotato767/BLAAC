# BLAAC documentation

## configuration

### voices

#### Using voices
This is currently unimplemented.

This program handles different voices pretty simply.
You choose the voice you want to use at any point.

Whenever you try to say something, BLAAC tries the following:

1. play an audio clip in your selected voice

2. read out a TTS message written in your selected voice

3. play an audio clip in your default voice

4. read a TTS message written for your default voice

5. play any audio clip

6. read any TTS message in its specified voice

7. read any TTS message in your default voice

8. use TTS to read out the name of the option

options 7 and 8 are fallback options, so BLAAC will warn you if they are used.

It is possible to specify TTS sentences and audio clips that work in multiple voices.

If you want one option to only be said in specific voices (e.g. you always want
to say "I am about to have a seizure" in a calm, neutral voice), remove any references
to other voices in that option's folder.

If you don't specify any voice for an audio clip or TTS message, it will not be
played if there is any voiced audio or TTS in the folder.
Audio without a specified voice is supported, because everyone should have the
ability to make a fart sound on command regardless of their disability. 

#### Adding new voices
Adding custom voices is a great way to become more expressive with this AAC.

To create a new voice, make a clip of you speaking in that voice for as close 
to thirty seconds as you can manage, with breaths removed from the audio.
The better quality the recording, the better the TTS will sound.
It also helps to have good phoneme variation.

Audacity is a free tool that can be used for recording and editing audio on PC.

If you are able to speak, saying "The quick brown fox jumps over the lazy dog" 
and then some phrases you would normally say in that voice is a good idea 
to start with, but do experiment.

If you are not, try to gather any audio clips that sound like the voice you want 
and splice them together into a 30 second long clip. It doesn't all have to be you,
but do get consent before using other people's voices.

Then, save it as a .wav and put it in the TTS voices folder. 
The voice name is whatever comes before the dot, and should contain only a-z, 0-9 and space.

For example, if I want to add a nervously excited voice:

1. I try to get myself speaking in the correct mood.

2. I record myself speaking for 30 seconds.

3. I save that recording as "nervously excited.wav" in the TTS voices folder.

Then the next time I start BLAAC, I will be able to select that voice.

After adding new voices, BLAAC will cache each of them to allow you to switch
between them very quickly. This process takes about 5 seconds per voice. 
These cached voices can be found in the chache subdirectory.

#### renaming/deleting/changing voices
If you make any changes to the audio file, 
*remember to delete the corresponding .safetensors file in the cache directory*.
This allows BLAAC to see that you have made a change and react to it.