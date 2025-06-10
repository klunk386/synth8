"""
Example: Simple SynthVoice with LFO and ADSR Modulation.

Creates a single voice using a sine wave oscillator, lowpass filter,
and a voltage-controlled amplifier. The gain is modulated by an ADSR
envelope, and frequency is modulated by an LFO.

Press 'z' to trigger the sound.
"""

from synth8.engine import SynthEngine
from synth8.voice import SynthVoice
from synth8.nodes import SynthOscillator, SynthFilter, SynthVCA
from synth8.modulators import SynthADSR, SynthLFO

# === Signal Path: Oscillator → Filter → VCA ===
osc = SynthOscillator(freq=261.63, waveform='sine')
filt = SynthFilter(cutoff=1200.0)
vca = SynthVCA(gain=1.0)

# === Modulators ===
env = SynthADSR(attack=0.03, decay=0.2, sustain=0.5, release=1.2)
lfo = SynthLFO(freq=5.0, depth=5.0, waveform='sine')

env.modulate(vca, param="gain")
lfo.modulate(osc, param="freq")

# === Voice ===
voice = SynthVoice()
voice.connect([osc, filt])
voice.connect(vca)
#voice.modulate(env, vca.param("gain"))
#voice.modulate(lfo, osc.param("freq"))

voice.add_modulator([env, lfo])

# === Engine ===
engine = SynthEngine()
engine.add_voice(voice, id='c_note', key='z')
engine.play(wait=True)
