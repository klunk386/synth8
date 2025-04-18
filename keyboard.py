"""
Keyboard Example – Real-Time Synth Trigger via QWERTY Layout

This example maps keyboard keys to musical notes (from C4 to E5) and assigns
a SynthVoice to each key. Voices share the same waveform, and optional
ADSR, filter, and LFO settings can be toggled via boolean flags.

Keys:
    z s x d c v g b h n j m , . /  → maps to C4 to E5

Press keys to trigger notes. Release to stop. Ctrl+C to quit.
"""

import time
from synth8 import SynthEngine, SynthVoice, TerminalSilent

# === GLOBAL SYNTH PARAMETERS ===
USE_FILTER = True
USE_ADSR = True
USE_LFO = True

WAVEFORM = 'sine'

ATTACK = 0.05
DECAY = 0.1
SUSTAIN = 0.6
RELEASE = 0.4

CUTOFF = 500

LFO_FREQ = 5.0
LFO_DEPTH = 2.0
LFO_WAVEFORM = 'sine'

# === NOTE FREQUENCIES (equal temperament, C4 = 261.63 Hz) ===
NOTE_FREQS = {
    'z': 261.63,  # C4
    's': 277.18,  # C#4
    'x': 293.66,  # D4
    'd': 311.13,  # D#4
    'c': 329.63,  # E4
    'v': 349.23,  # F4
    'g': 369.99,  # F#4
    'b': 392.00,  # G4
    'h': 415.30,  # G#4
    'n': 440.00,  # A4
    'j': 466.16,  # A#4
    'm': 493.88,  # B4
    ',': 523.25,  # C5
    '.': 587.33,  # D5
    '/': 659.26   # E4
}

# === SETUP ENGINE AND VOICES ===
engine = SynthEngine()

for key, freq in NOTE_FREQS.items():
    voice = SynthVoice()
    voice.oscillator(freq=freq, waveform=WAVEFORM)

    if USE_FILTER:
        voice.lowpass(cutoff=CUTOFF)

    if USE_ADSR:
        voice.adsr(attack=ATTACK, decay=DECAY,
                   sustain=SUSTAIN, release=RELEASE)

    if USE_LFO:
        voice.lfo(freq=LFO_FREQ, depth=LFO_DEPTH, waveform=LFO_WAVEFORM)

    engine.add_voice(voice, id=key.upper(), key=key)

engine.play()

print("Play the keyboard! (Z-M)")
print("Press CTRL+C to stop.")

try:
    with TerminalSilent():
        while True:
            time.sleep(0.01)
except KeyboardInterrupt:
    engine.stop()
    print("Stopped.")

