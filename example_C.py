"""
Chord Example – Real-Time Synthesizer in Python

This example demonstrates how to create and play a C major chord using
the SynthEngine, SynthVoice, and Mixer classes.
"""

import time
from synth8 import SynthVoice, Mixer, SynthEngine, TerminalSilent

# Frequencies for a C major chord: C4, E4, G4
FREQS = [261.63, 329.63, 392.00]

# Create the voices
voices = []
for freq in FREQS:
    voice = SynthVoice()
    voice.oscillator(freq=freq, waveform='sine')
    voice.adsr(attack=0.05, decay=0.1, sustain=0.7, release=0.4)
    voices.append(voice)

# Combine them into a mixer
chord = Mixer(voices)

# Initialize the synth engine
engine = SynthEngine()
engine.add_voice(chord, id='C_MAJOR', key='z')
engine.play()

# Interactive keyboard control
print("Press 'z' to play a C major chord. Press Ctrl+C to exit.")

try:
    with TerminalSilent():
        while True:
            time.sleep(0.01)
except KeyboardInterrupt:
    engine.stop()
    print("Goodbye!")

