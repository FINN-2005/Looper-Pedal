# Looper-Pedal

A simple real-time audio looper pedal built in Python with delay, overdubbing, and live playback.

# Description

This project is an experimental attempt to recreate a guitar looper pedal in Python.  
It captures live audio input, applies a configurable delay to compensate for device latency, and lets you record an initial loop, overdub new layers, play back continuously, and clear the loop entirely.  
The system is built using sounddevice, processes audio in real time through callbacks, and uses keyboard controls to mimic the workflow of a physical looping pedal.  

# Installation

- git clone
- install dependencies
  ```bash
  pip install sounddevice numpy keyboard
  ```
# Usage

Run the script:  
  ``` python looper.py ```
Controls:  
- SPACE → Start first recording / stop and set loop length / toggle overdub mode
- C → Clear the current loop  
- Q → Quit the program  
Workflow:  
- Press SPACE to begin the first recording.  
- Press SPACE again to close the loop — playback begins immediately.  
- Press SPACE again to toggle overdubbing (layering).  
- Press C to erase everything and start over.  
A short delay (defined in delay_ms) compensates for microphone + driver latency to keep loops aligned.  
  

