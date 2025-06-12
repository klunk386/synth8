# synth8

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Python >=3.8](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Status: Beta](https://img.shields.io/badge/status-beta-yellow)]()
[![GitHub Repo](https://img.shields.io/badge/github-relievo-lightgrey?logo=github)](https://github.com/yourname/relievo)

<p align="center">
  <img src="logo/logo_small.png" alt="synth8 logo" width="300"/>
</p>

`synth8` is a real-time modular synthesizer engine built entirely in Python.  
It enables musicians, sound designers, and developers to build and control audio synthesis chains using signal modules, modulators, and dynamic voice routing.

Designed for minimal latency and high flexibility, `synth8` is ideal for prototyping instruments, implementing educational tools, or serving as a backend for MIDI-controlled environments (via the upcoming `klavio` library).

---

## Features

- Modular node-based signal processing (oscillators, filters, VCAs)
- ADSR envelopes and LFO modulation
- Real-time playback with <10 ms latency
- Keyboard-to-voice mapping (via QWERTY)
- Automatic voice deactivation and cleanup
- Stereo output with volume normalization
- Designed to be extended and embedded

---

## Installation

### Requirements

- Python 3.8+
- `numpy`
- `scipy`
- `sounddevice`
- `pynput`

### From PyPI (upcoming)

```bash
pip install synth8
```

### From source

```bash
git clone https://github.com/yourname/synth8
cd synth8
pip install .
```

Or for development:

```bash
pip install -e .
```

---

## Library Overview

```
 SynthEngine
    ├── manages voices and audio output
    ├── maps keyboard events to voice IDs
    │
    └── SynthVoice(s)
         ├── connects signal modules (osc → filt → vca)
         ├── supports modulation via ADSR, LFO
         └── handles gate_on / gate_off logic
```

Modules include:

- `SynthOscillator` (sine, square, saw)
- `SynthFilter` (2nd-order lowpass)
- `SynthVCA` (gain-controlled amplifier)
- `SynthADSR` (vectorized envelope)
- `SynthLFO` (cyclical modulation)

---

## Usage Examples

### 1. Minimal oscillator voice

```python
from synth8 import SynthEngine, SynthVoice, SynthOscillator

osc = SynthOscillator(freq=440, waveform='sine')
voice = SynthVoice()
voice.connect(osc)

engine = SynthEngine()
engine.add_voice(voice, id='note_a', key='z')
engine.play(wait=True)
```

### 2. Add filter and VCA

```python
from synth8.nodes import SynthFilter, SynthVCA

osc = SynthOscillator(freq=440)
filt = SynthFilter(cutoff=1000)
vca = SynthVCA(gain=1.0)

voice = SynthVoice()
voice.connect([osc, filt, vca])
```

### 3. Add ADSR envelope and LFO

```python
from synth8.modulators import SynthADSR, SynthLFO

adsr = SynthADSR(attack=0.01, decay=0.1, sustain=0.8, release=0.3)
lfo = SynthLFO(freq=5.0, depth=4.0)

adsr.modulate(vca, "gain")
lfo.modulate(osc, "freq")

voice.add_modulator([adsr, lfo])
```

---

## Keyboard Mapping

Voices are mapped to keyboard keys using:

```python
engine.add_voice(voice, id="note_c", key="z")
```

- On press → `voice.trigger_on()`
- On release → `voice.trigger_off()`

Run this example:

```bash
python examples/keyboard_piano.py
```

Or try `example_chord.py` for a simple chord test.

---

## Performance Notes

- Default block size: 512 samples
- Latency: 0.01 seconds
- Vectorized processing for ADSR and LFO
- Volume scaling with `1 / sqrt(active_voices)` avoids clipping

---

## Extending synth8

`synth8` is designed to be modular and expandable:

- Add new node types: filters, waveshapers, delays
- Create custom modulators
- Integrate GUI or OSC control
- MIDI integration planned via `klavio`

---

## License

This project is licensed under the **GNU AGPL v3** license.

---

## Author

**Valerio Poggi** 2025
