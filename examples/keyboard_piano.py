"""
Synth8 – Keyboard Piano Example

Maps computer keyboard keys to musical notes using modular SynthVoice
instances. Demonstrates oscillator → filter → VCA chain with envelope
and optional LFO modulation.

Author: Valerio Poggi – 2025
"""

import time
from synth8.engine import SynthEngine
from synth8.voice import SynthVoice
from synth8.nodes import SynthOscillator, SynthFilter, SynthVCA
from synth8.modulators import SynthADSR, SynthLFO

# --- Note mapping: QWERTY layout to MIDI-like notes ---
KEY_TO_FREQ = {
    'z': 261.63,  # C4
    'x': 293.66,  # D4
    'c': 329.63,  # E4
    'v': 349.23,  # F4
    'b': 392.00,  # G4
    'n': 440.00,  # A4
    'm': 493.88,  # B4
    ',': 523.25,  # C5
}

# --- Synth defaults ---
WAVEFORM = 'saw'
CUTOFF = 1200
ENV = dict(attack=0.01, decay=0.1, sustain=0.7, release=0.3)
LFO = dict(freq=5.0, depth=4.0, waveform='sine')

# --- Engine setup ---
engine = SynthEngine()

for key, freq in KEY_TO_FREQ.items():
    # Signal path: osc → filter → VCA
    osc = SynthOscillator(freq=freq, waveform=WAVEFORM)
    filt = SynthFilter(cutoff=CUTOFF)
    vca = SynthVCA(gain=1.0)

    voice = SynthVoice()
    voice.connect([osc, filt, vca])

    # Envelope → VCA.gain
    adsr = SynthADSR(**ENV)
    adsr.modulate(vca, "gain")

    # Optional LFO → OSC.freq
    lfo = SynthLFO(**LFO)
    lfo.modulate(osc, "freq")

    voice.add_modulator([adsr, lfo])

    # Register to engine
    engine.add_voice(voice, id=f"note_{key}", key=key)

# --- Run ---
print("Press keys Z-M to play notes. Ctrl+C to stop.")
engine.play(wait=True)

