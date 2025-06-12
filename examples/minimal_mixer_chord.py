"""
Example: Mixing multiple independent SynthVoice instances.

Plays a C major chord (C4, E4, G4) when key 'z' is pressed.
Each note is a separate voice managed by a Mixer.
"""

from synth8.engine import SynthEngine
from synth8.voice import SynthVoice, Mixer
from synth8.nodes import SynthOscillator, SynthFilter, SynthVCA
from synth8.modulators import SynthADSR

# Define note frequencies
frequencies = [261.63, 329.63, 392.00]  # C4, E4, G4

# Create voices for each note
voices = []

for freq in frequencies:
    osc = SynthOscillator(freq=freq, waveform='saw')
    filt = SynthFilter(cutoff=1200)
    vca = SynthVCA(gain=0.0)

    adsr = SynthADSR(attack=0.02, decay=0.15, sustain=0.7, release=0.5)
    adsr.modulate(vca, "gain")

    voice = SynthVoice()
    voice.connect([osc, filt, vca])
    voice.add_modulator(adsr)

    voices.append(voice)

# Combine with Mixer
mixer = Mixer(gain=1.0)
for v in voices:
    mixer.add_voice(v)

# Register mixer as one voice
engine = SynthEngine()
engine.add_voice(mixer, id='c_major_chord', key='z')
engine.play(wait=True)
