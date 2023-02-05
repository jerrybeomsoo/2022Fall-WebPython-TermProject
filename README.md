# 2022 Fall Semester Kyung Hee University SWCON Web/Python Programming Term Project
WAV audio file header processing / sample interpolation

**main.py** is the original code written/submitted for the "Term Project".

**splineInterpolator.py** is the modified version of the former, to support 24bit / stereo audio, and to be used for upsampling.

## main.py
1. Randomly fetches an WAV audio file (PCM 8bit / 16000Hz / Mono) from MS-SNSD github repo
2. Processes the header and extracts the audio samples one-by-one
3. Truncates audio sample to 8000Hz by removing even number samples
4. Interpolates truncated audio samples by linear, spline, and random-fill methods
5. Edits the WAV header to match new audio samples and writes the WAV file
6. Outputs visual representation of the original 16kHz sample and interpolated-to-16kHz audio using spectrogram

## splineInterpolator.py
1. Opens a WAV file and sets the muliplication rate selected by user
2. Processes the header and extracts the audio samples one-by-one
3. Interpolates the original audio samples by the multiplication rate (2 or 4)
4. Edits the WAV header to match new audio samples and writes the WAV file

### The purpose of writing this little, useless, dirty piece of code :
1. Understanding of WAV file structure and PCM format - how header and samples work
2. Basic comprehension of audio processing: Simple audio downscaling by removing samples does NOT work, due to aliasing- a low-pass filter is required to get anti-aliased results.
