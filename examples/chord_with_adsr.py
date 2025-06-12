"""
Example: Chord-like sound with multiple oscillators and shared ADSR.

This example creates a SynthVoice with three oscillators (C4, E4, G4),
combined into a single voice using a shared envelope and VCA.
The envelope controls the amplitude with a soft pad-like shape.

Key mapping:
    z → C major chord with ADSR envelope
"""

from synth8.engine import SynthEngine
from synth8.voice import SynthVoice
from synth8.nodes import SynthOscillator, SynthVCA
from synth8.modulators import SynthADSR

osc1 = SynthOscillator(freq=261.63, waveform='sine')  # C4
osc2 = SynthOscillator(freq=329.63, waveform='sine')  # E4
osc3 = SynthOscillator(freq=392.00, waveform='sine')  # G4

vca = SynthVCA(gain=0.0)

adsr = SynthADSR(attack=0.2, decay=0.5, sustain=0.6, release=1.5)
adsr.modulate(vca, "gain")

voice = SynthVoice()
voice.connect([osc1, osc2, osc3])
voice.connect(vca)
voice.add_modulator(adsr)

engine = SynthEngine()
engine.add_voice(voice, id='adsr_chord', key='z')
engine.play(wait=True)
