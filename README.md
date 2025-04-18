# Python Synth8

A modular synthesizer engine for real-time audio synthesis in Python.

This system supports multiple voices (polyphony) with independent waveform
generators (oscillators), ADSR envelopes, low-pass filters, and LFO modulation.
Voices can be triggered as API call or keyboard via keys (using `pynput`).

---

## Features

- Real-time audio synthesis using `sounddevice`
- Basic waveforms: sine, square, saw
- ADSR amplitude envelope (attack, decay, sustain, release)
- LFO modulation (vibrato/frequency modulation)
- Per-key voice triggering using keyboard binding
- Cross-platform terminal handling (Unix and Windows)

---

## Installation

You need Python 3.8+ and the following packages:

```bash
pip install numpy sounddevice scipy pynput
```

---

## Example Usage

```python
from synth8 import SynthVoice, SynthEngine, TerminalSilent
import time

voice1 = SynthVoice()
voice1.oscillator(freq=261.6, waveform='saw')
voice1.lowpass(cutoff=1000)
voice1.adsr(attack=0.05, decay=0.2, sustain=0.5, release=0.5)
voice1.lfo(freq=6.0, depth=8.0, waveform='sine')

voice2 = SynthVoice()
voice2.oscillator(freq=293.7, waveform='square')
voice2.lowpass(cutoff=1200)
voice2.adsr(attack=0.02, decay=0.1, sustain=0.4, release=0.6)
voice2.lfo(freq=5.0, depth=4.0, waveform='triangle')

engine = SynthEngine()
engine.add_voice(voice1, id='A', key='z')
engine.add_voice(voice2, id='B', key='x')

engine.play()

with TerminalSilent() as ts:
    print("Press 'z' or 'x' to play (CTRL+C per exit).")
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        engine.stop()
        print("Bye!")
```
---

## License

This project is licensed under the **GNU General Public License v3.0 (GPLv3)**.

See the LICENSE file or visit [https://www.gnu.org/licenses/gpl-3.0.html](https://www.gnu.org/licenses/gpl-3.0.html) for details.

---

## Author

Valerio Poggi — 2025


