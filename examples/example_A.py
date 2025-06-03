"""
Voice Sequencing Example – Play Individual Notes in Time

This example demonstrates how to trigger multiple SynthVoice instances
independently in time. Three sine wave voices corresponding to C, E, and G
are added to the SynthEngine and played in sequence to build a chord
gradually, then released after a delay.
"""

import time
from synth8 import SynthVoice, SynthEngine

# C
voice1 = SynthVoice()
voice1.oscillator(freq=261.63, waveform='sine')

# E
voice2 = SynthVoice()
voice2.oscillator(freq=329.63, waveform='sine')

# G
voice3 = SynthVoice()
voice3.oscillator(freq=392.00, waveform='sine')

engine = SynthEngine()

engine.add_voice(voice1, id='A')
engine.add_voice(voice2, id='B')
engine.add_voice(voice3, id='C')

engine.play()

engine.voice_on('A')
time.sleep(1)
engine.voice_on('B')
time.sleep(1)
engine.voice_on('C')
time.sleep(5)

engine.voice_off('A')
engine.voice_off('B')
engine.voice_off('C')

engine.stop()
