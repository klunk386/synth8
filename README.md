# synth8

[![License: AGPL v3](https://img.shields.io/badge/license-AGPLv3-blue)](https://www.gnu.org/licenses/agpl-3.0)
[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![Status](https://img.shields.io/badge/status-beta-yellow.svg)]()
[![Repository](https://img.shields.io/badge/github-synth8-black?logo=github)](https://github.com/yourname/synth8)

<p align="center">
  <img src="logo/logo_small.png" alt="synth8 logo" width="300"/>
</p>

`synth8` is a modular synthesizer engine implemented in pure Python for real-time sound synthesis.  
It is designed for musicians and developers who want full programmatic control over how sounds are generated, modulated, and triggered.

With `synth8`, you can define signal chains by combining oscillators, filters, VCAs, and modulation sources such as envelopes and LFOs. Each signal chain is managed as a **voice**, which can be triggered by keyboard events or programmatically.  
The architecture is simple, extensible, and designed with future integration (e.g. MIDI via `klavio`) in mind.

---

## Features

- Modular signal architecture: oscillators, filters, amplifiers, modulators
- Real-time low-latency audio output via `sounddevice`
- QWERTY keyboard control with press/release handling
- ADSR envelopes and LFOs for time-based and cyclical modulation
- Fully programmatic voice creation and connection
- Dynamic voice activation and automatic cleanup
- Mixer class to combine layered voices or chords
- Easily extensible for new signal types or control inputs

---

## Installation

### Requirements

- Python 3.8 or higher
- numpy
- scipy
- sounddevice
- pynput

Install dependencies (if not already available):

```bash
pip install numpy scipy sounddevice pynput
```

### Install from PyPI (planned)

```bash
pip install synth8
```

### Install from source

```bash
git clone https://github.com/yourname/synth8
cd synth8
pip install .
```

For development:

```bash
pip install -e .
```

---

## Library Overview

`synth8` is built around the idea of **modular signal flow**. A central `SynthEngine` manages a collection of independent sound-producing **voices**, each of which is composed of interconnected **nodes** and optionally controlled by **modulators**.

### What is a Voice?

A **SynthVoice** is a self-contained audio processing chain — typically corresponding to a single note or instrument voice — that defines:

- One or more **nodes**: components like oscillators, filters, VCAs
- One or more **modulators**: components that modify parameters over time (e.g., envelopes, LFOs)
- A logical gate state: whether the voice is currently active, controlled by key press/release

Each voice can be mapped to a keyboard key, or triggered programmatically. When the key is released, the voice enters a release phase and is automatically deactivated.

**Minimal example** — a sine oscillator controlled via the 'z' key:

```python
from synth8 import SynthEngine, SynthVoice, SynthOscillator

osc = SynthOscillator(freq=440, waveform='sine')
voice = SynthVoice()
voice.connect(osc)

engine = SynthEngine()
engine.add_voice(voice, id='note_a', key='z')
engine.play(wait=True)
```

---

### Nodes: Oscillator → Filter → VCA

**Nodes** are audio processors arranged in sequence. The most common nodes are:

- `SynthOscillator`: waveform generator (`sine`, `square`, `saw`)
- `SynthFilter`: second-order low-pass filter
- `SynthVCA`: voltage-controlled amplifier for amplitude control

**Example: adding filter and amplifier**

```python
from synth8.nodes import SynthFilter, SynthVCA

osc = SynthOscillator(freq=440)
filt = SynthFilter(cutoff=1000)
vca = SynthVCA(gain=1.0)

voice = SynthVoice()
voice.connect([osc, filt, vca])
```

---

### Modulators: ADSR and LFO

**Modulators** are control sources that affect node parameters over time. They include:

- `SynthADSR`: envelope with attack, decay, sustain, release
- `SynthLFO`: low-frequency oscillator for vibrato, tremolo, etc.

Modulators are connected to a node’s parameter using:

```python
modulator.modulate(target_node, "parameter_name")
```

**Example: envelope on gain and LFO on frequency**

```python
from synth8.modulators import SynthADSR, SynthLFO

adsr = SynthADSR(attack=0.01, decay=0.1, sustain=0.8, release=0.3)
lfo = SynthLFO(freq=5.0, depth=4.0)

adsr.modulate(vca, "gain")
lfo.modulate(osc, "freq")

voice.add_modulator([adsr, lfo])
```

---

### Keyboard Triggering

`synth8` maps voices to keys using the `add_voice()` method:

```python
engine.add_voice(voice, id="note_c", key="z")
```

- On press: `voice.trigger_on()` is called
- On release: `voice.trigger_off()` triggers the release phase
- Multiple voices can be assigned to different keys (e.g. piano layout)

---

### Mixer: Combining Multiple Voices

A `Mixer` combines several `SynthVoice` instances and acts like a single voice. It is useful to play chords or layered instruments with a single key.

**Example: chord with three voices (C, E, G)**

```python
from synth8.voice import Mixer

# Define three independent voices
voice1 = SynthVoice()
voice2 = SynthVoice()
voice3 = SynthVoice()

# Connect oscillators, filters, VCAs, modulators to each voice...

# Combine into one logical voice
mixer = Mixer(gain=1.0)
mixer.add_voice(voice1)
mixer.add_voice(voice2)
mixer.add_voice(voice3)

engine.add_voice(mixer, id="c_major", key="z")
```

---

## Full Demos

| File                          | Description                                                                 |
|------------------------------|-----------------------------------------------------------------------------|
| `keyboard_piano.py`          | QWERTY piano (Z to ,) with separate voices, each using ADSR + LFO          |
| `example_simple.py`          | Single voice with oscillator → filter → VCA, modulated by ADSR + LFO       |
| `minimal_mixer_chord.py`     | Chord (C–E–G) using a Mixer with 3 independent voices                      |
| `lfo_only_tremolo.py`        | A sine oscillator modulated by an LFO on gain (tremolo effect)             |

All examples are located in the `examples/` directory and can be run directly with:

```bash
python examples/<filename>.py
```

---

## Extending `synth8`

`synth8` is modular by design. You can extend it in several directions:

- Create new signal nodes: bandpass filters, distortion units, custom oscillators
- Add new modulators: sequencers, step envelopes, MIDI-controlled curves
- Integrate with GUI controls or network protocols (e.g. OSC)
- Add MIDI support via the upcoming `klavio` library

The codebase is clean and lightweight, making it easy to prototype new behaviors or integrate into a larger system.

---

## License

This project is released under the **GNU Affero General Public License v3.0 (AGPL-3.0)**.

---

## Author

**Valerio Poggi** - 2025
