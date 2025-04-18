"""
Multi-Voice Keyboard Example – Real-Time Synth Control with LFO and Filtering

This example demonstrates how to assign multiple SynthVoice instances to
different keyboard keys using SynthEngine. Each voice has its own waveform,
filter, ADSR envelope, and LFO settings. Use the 'z' and 'x' keys to trigger
the two voices in real-time.
"""

import time
from synth8 import SynthVoice, SynthEngine, TerminalSilent

# === Voice 1: Saw wave with sine LFO on pitch
voice1 = SynthVoice()
voice1.oscillator(freq=261.6, waveform='saw')
voice1.lowpass(cutoff=1000)
voice1.adsr(attack=0.05, decay=0.2, sustain=0.5, release=0.5)
voice1.lfo(freq=6.0, depth=8.0, waveform='sine')

# === Voice 2: Square wave with triangle LFO on pitch
voice2 = SynthVoice()
voice2.oscillator(freq=293.7, waveform='square')
voice2.lowpass(cutoff=1200)
voice2.adsr(attack=0.02, decay=0.1, sustain=0.4, release=0.6)
voice2.lfo(freq=5.0, depth=4.0, waveform='triangle')

# === Engine setup
engine = SynthEngine()
engine.add_voice(voice1, id='VOICE_Z', key='z')
engine.add_voice(voice2, id='VOICE_X', key='x')
engine.play()

# === Interactive control via keyboard
print("Press 'z' or 'x' to play voices. Press Ctrl+C to exit.")

try:
    with TerminalSilent():
        while True:
            time.sleep(0.01)
except KeyboardInterrupt:
    engine.stop()
    print("Goodbye!")

