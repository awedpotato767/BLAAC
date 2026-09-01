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
- speech contains all of your configured boards.
- config/presets contains some default board options.

## What you are allowed to do with this project.

Do what you want. Just don't hurt the disabled community with it or force people to pay to customise their copy of this project.
I welcome remixing, forking, modifying, changing and otherwise messing around with this code. All I ask is that people get linked back to this document.

To the maximum extent allowed by the law, I am not responsible for what other people do with this code, and I ask that people respect the licenses and wishes of the developers of the dependencies of this project, as they do differ. In particular, pocket-tts. That is the foundation behind the fancy voices you hear. Don't be a dickhead and ruin this technology for the rest of us.

This code is released under the CC BY-SA license. Basically, mention where you got the code from, and don't bundle it into proprietary systems under a more restrictive license.
