# BLAAC documentation

## configuration

### audio devices

In global config.toml, the options default_speaker and default_headphones determine which devices BLAAC attempts to use upon boot.
Both are either a numerical ID determining which device is used (not recommended), or a substring of the device name (recommended).

default_speaker is the device that your voice should come out of when the program boots.
default_headphones is the device that any audio feedback should come through.

If these are set to the same value, both will play from the same device. TODO this needs a better implementation.

### audio feedback
Each of these options are found in the global settings document.

#### navigation

This has four levels:

1. On focus (default)

    - BLAAC reads each item out when it is focussed.

2. On selection

    - BLAAC reads each item out when it is selected.

3. Chimes

    - BLAAC plays different chimes for successfully entering a new menu, 
    moving your focus, and 
    going to the top level menu.

4. Off

#### typing

1. On space

2. On keypress

3. Off

### voices

#### Using voices
This is currently unimplemented.

This program handles different voices pretty simply.
You choose the voice you want to use at any point.

Whenever you press a button, out of the box, BLAAC tries the following: 

1. play a random sound file associated with your current voice.

2. say a random TTS message associated with that voice.

4. play the standard sound associated with that button.

3. say the default vocalisation associated with the button in that voice.

4. speak the button label in your current voice.

If you want BLAAC to prioritise the TTS over individual sounds, change the option in the global config for now.

ext_BLAAC_force_voice can be specified at the board or button level to force specific intonation.
Button voice overrides board voice which overrides chosen voice.



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

## usage

### menu navigation
UNIMPLEMENTED

There are five menu navigation modes by default: coordinates, smart, search, tab navigation
and scanning.

In general, move your focus to an item and press space to select it.
The enter key reads out the whole sentence.
z undoes the last action, x deletes the entire sentence, and c deletes the last word.


#### coordinates

Press the character corresponding to which column it is in (left to right), then which row it is in (top to bottom) for grid layout boards.

By default, this is 1-9, 0 counts as 10, - as 11, = as 12.

So for an item in the first row and fifth column, press one, five, space.

For six-key input users, there will "qwerty six-key mode" and "hable six-key mode" - where the numerical indeces are replaced with the first letters of the alphabet.
Qwerty six-key mode is strictly for navigation, it is not enabled while searching or typing sentences.

#### direct

This is not enabled by default, but allows certain keys and key combinations to be permanently mapped to portions of the grid (option configured per board).

#### Search 

This is a stable method of accessing menu items, but is also somewhat slow.
Only items matching the entered text can be selected, starting with items that 
start with the search text and sorted alphabetically.

#### Tab navigation

default shortcuts:
Tab to move one botton to the right. Left to right, then top to bottom.
Q to move one row down. Top to bottom, then left to right.

Shift plus either reverses direction.

#### W A S D and arrow navigation

W - up
S - down
A - left
D - right

This navigation mode does not wrap. If six-key mode is enabled, this navigation mode is disabled.


#### Scanning mode

This is equivalent to pressing tab at fixed intervals. Press enter to select the
current option.



#### On demand

By default, there will be several shortcuts to read out information on where you are.

p - reads out the path from home to your current board
b - reads out the name of the current board
t - reads the current time
i - reads out some key settings, such as whether six key mode is enabled, and lists some essential shortcuts

### Speech

By default, BLAAC says each word as it comes, then pressing enter says the whole sentence.

## Techinical details

BLAAC is split into several modules.

- audioHandler
- UI
- board management

### audioHandler

This actor is the ony thing that touches any audio device. Text and audio data go in, speech and sound come out.
These actors have a bad habit of failing silently, so if you want to get an error, please use a blocking operation to inspect.

Contains one class:

audioHandler(pykka.ThreadingActor)

Attributes:

- current_voice
- output_device
- output_channels (1 or 2)
- usually_interrupt - either say everything as soon as the message comes, or wait.
- volume

API:

- say(text, voice=class default, volume=class defualt, interrupt=class default)
    - Synthesises a TTS voice and plays it through the class output.
    - Modifying the defaults is preferred, rather than overriding.
- play(audio, volume=class default, interrupt=class default)
    - if audio is a string, audioHandler will assume it is a filepath and attempt to play that.
    - if audio is a numpy array, audioHandler will attempt to play it as raw audio through the sounddevice backend.
- get_voices()
    - returns a list of valid voice names.
- load_voice_dir(dirpath)
    - attempts to load all precached voices in a given directory and a cache/ subdirectory if one  exists.
- preprocess_voice_dir(dirpath)
    - attempts to cache any voices that the model has not loaded yet into cache/.
    
Use *one* and exactly one instance of this class per audio output. Failing to do so will lead to bad times.
FIXME

### Board management

This is a three-class module.

class button:

attributes (following the JSON schema closely):

- image_id
- label
- vocalisation
- ext_BLAAC_force_voice
- ext_BLAAC_alternate_vocalisations
- sound_id
- ext_BLAAC_alternate_sounds
- load_board
- action
- actions
- text_color = None - currently unused in the spec
- background_color
- border_color


// cannot assume uniqueness of IDs outside of the specific board

class board:

attributes:

- format
- id
- locale
- url
- name
- description_html
- buttons
- grid
- sounds
- images
- strings
- ext_BLAAC_force_voice

class manifest:

- format
- root
- boards
- images
- sounds
