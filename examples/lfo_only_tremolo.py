"""
Example: Tremolo effect using LFO on VCA gain.

Plays a continuous sine wave with volume modulation (tremolo) when 'z' is pressed.
No envelope is used.
"""

from synth8.engine import SynthEngine
from synth8.voice import SynthVoice
from synth8.nodes import SynthOscillator, SynthVCA
from synth8.modulators import SynthLFO

osc = SynthOscillator(freq=440, waveform='sine')
vca = SynthVCA(gain=1.0)

lfo = SynthLFO(freq=5.0, depth=0.5, waveform='sine')
lfo.modulate(vca, "gain")

voice = SynthVoice()
voice.connect([osc, vca])
voice.add_modulator(lfo)

engine = SynthEngine()
engine.add_voice(voice, id='tremolo_sine', key='z')
engine.play(wait=True)
