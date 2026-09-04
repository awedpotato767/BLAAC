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

## planned architecture.

See Documentation.md in this directory for more in depth information.

### User interface:

Initially, a text user interface with keyboard and pointer support combined with inbuilt screen reader.
Long term, optional GUI presentation and support for gaze tracking/ear rumble/gesture based input.

### backend:

In short, separated modules for audio output, board management and user interface.

## What you are allowed to do with this project.

I welcome remixing, forking, modifying, changing and otherwise messing around with this code. All I ask is that people get linked back to this document.

To the maximum extent allowed by the law, I am not responsible for what other people do with this code, and I ask that people respect the licenses and wishes of the developers of the dependencies of this project, as they do differ. In particular, pocket-tts. That is the foundation behind the fancy voices you hear.

This code is released under the CC BY-SA license. Basically, mention where you got the code from, and don't bundle it into proprietary systems under a more restrictive license.
