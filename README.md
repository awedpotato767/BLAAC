# BLAAC
### A custom key chording-based AAC written in Python.

NOTICE: THIS IS NOT CURRENTLY USABLE.

## Goals

To create a Voice Output Communication Aid (VOCA) that feels unobtrusive and undemanding, yet natural to use.

Must be compatible with the open board format's [specifications](https://www.openboardformat.org/) and accomplish many of openAAC's design [considerations](https://www.openaac.org/considerations).

Current priorities:
- Sightless accessibility
- Comfort over extended conversations
- Natural speech

Ideally, the preformance should be such that BLAAC can reasonably be run portably over a 24hr period. 
That is a medium-term goal, once good usability has been achieved.

This project has not had any real-world testing yet, so any volunteers are welcome to help clarify the project's direction.

## Installation

This is currently alpha software, so these  are liable to change.
All python files are designed to be run from the project root. They will raise an error if fun from elsewhere.

### linux

requirements:

- python
- git

Alternately, you can extract the code manually, but this makes updates harder.

    > git clone git@github.com:awedpotato767/BLAAC.git
    > cd BLAAC/
    > ./src/venv_setup_linux.sh
    
To run the code:

    > #run once per session
    > cd BLAAC/
    > source .venv/bin/activate
    > python BLAAC.py
    
### MacOS/Windows

These are currently untested, but I recommend following the normal steps to install a virtual environment from the provided requirements.txt.

Please submit any bugs for these systems, but they will be low-priority until we get to MVP stage.

## planned architecture.

See Documentation.md in this directory for more in depth information.

### User interface:

Initially, a text user interface with keyboard and pointer support combined with inbuilt screen reader.
Long term, optional GUI presentation and support for gaze tracking/ear rumble/gesture based input.

### backend:

In short, separated modules for audio output, board management and user interface.

## What you are allowed to do with this project.

I welcome remixing, forking, modifying, changing and otherwise messing around with this code. All I ask is that people get linked back to this document.

This means that I do not welcome scraping this data for reuse by LLMs, and I do recommend people interact with this codebase without LLMs, since it is pretty complex and LLM hallucination will be hard to spot.

To the maximum extent allowed by the law, I am not responsible for what other people do with this code, and I ask that people respect the licenses and wishes of the developers of the dependencies of this project, as they do differ. In particular, pocket-tts. That is the foundation behind the fancy voices you hear.

This code is released under the CC BY-SA license. Basically, mention where you got the code from, and don't bundle it into proprietary systems under a more restrictive license.
