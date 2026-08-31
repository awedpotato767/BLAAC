# BLAAC
### A custom key chording-based AAC written in Python.

NOTICE: THIS IS NOT CURRENTLY USABLE.

## Goals

To create a Voice Output Communication Aid (VOCA) that feels unobtrusive and undemanding.
With recent advances in voice banking and cloning, I feel that voice dysphoria from AAC use is not an inevitability.
Hence this project puts customisation first, and aims to support features like randomised voice samples, custom emotions and raising your voice.


Priorities:
- Sightless use
- Comfort over extended conversations
- Natural speech

## planned architecture.

### User interface:
A text-based UI that captures full keyboard input and has both a screen reader system and tab navigation for learning purposes.
This will be menu based and allow key chording, enabling fast navigation to shortcuts like "TTS input" and "vocal tone". Yes, this means you can add a darth vader voice hotkey if you wish.
### backend:
There will be a global backup configuration, and the rest will be done through directory structures and text files.

I plan for a structure like the following:
In the root directory, there will be four folders. Config, tts voices, speech and src.
- Global configuration will be done in config. 
- tts voices will contain any files used by the TTS system to replicate your desired voices.
- speech will be where most of the setup time will be. 
 - This is where you set up the menu system and store prerecorded voice samples for direct use.
 - Each folder will contain a file listing any custom shortcuts to subfolders, audio files to be played upon entry to the folder, and/or text to be read by your TTS upon entry to the subfolder.

## What you are allowed to do with this project.

Do what you want. Just don't hurt the disabled community with it or force people to pay to customise their copy of this project.

I want you to be able to create your own voice within this tool, and this is why I have chosen to release it under Creative Commons Attribution-ShareAlike (CC BY-SA).
I welcome remixing, forking, modifying, changing and otherwise messing around with this code. All I ask is that people get linked back to this document.

