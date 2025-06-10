"""
Modulation Sources for Modular Synthesizer.

This module defines time-varying control signals such as envelopes and
low-frequency oscillators, usable for modulating audio module parameters.

Author: Valerio Poggi - 2025
"""

from synth8.engine import SAMPLE_RATE

import numpy as np


class SynthModulator:
    """
    Base class for modulation sources.
    """

    def __init__(self):
        self.targets = []

    def modulate(self, target, param):
        """
        Connects this modulator to a module's parameter.

        Parameters:
            target (object): Synth module instance.
            param (str): Name of the parameter to modulate.
        """
        self.targets.append((target, param))

    def trigger_on(self):
        """
        Optional: starts time-based modulation (e.g., envelope).
        """
        pass

    def trigger_off(self):
        """
        Optional: initiates release phase.
        """
        pass

    def render(self, frames):
        """
        Computes the modulation signal and routes it to all targets.

        Parameters:
            frames (int): Number of samples to generate.
        """
        raise NotImplementedError("Subclasses must implement render().")


class SynthADSR(SynthModulator):
    """
    Standard ADSR envelope generator with vectorized rendering.
    """

    def __init__(self, attack=0.01, decay=0.1,
                 sustain=0.7, release=0.3,
                 sample_rate=SAMPLE_RATE):
        super().__init__()
        self.attack = float(attack)
        self.decay = float(decay)
        self.sustain = float(sustain)
        self.release = float(release)
        self.sample_rate = sample_rate

        self.env_phase = 'off'
        self.env_level = 0.0
        self.active = False

    def trigger_on(self):
        self.env_phase = 'attack'
        self.env_level = 0.0
        self.active = True

    def trigger_off(self):
        if self.env_phase != 'off':
            self.env_phase = 'release'

    def render(self, frames):
        out = np.zeros(frames, dtype=np.float32)
        sr = self.sample_rate

        t = np.arange(frames) / sr
        level = self.env_level

        i = 0
        while i < frames:
            remaining = frames - i
            if self.env_phase == 'attack':
                dur = max(int(self.attack * sr), 1)
                step = 1.0 / dur
                n = min(dur, remaining)
                env = level + step * np.arange(n)
                env = np.clip(env, 0.0, 1.0)
                out[i:i+n] = env
                level = env[-1]
                i += n
                if level >= 1.0:
                    level = 1.0
                    self.env_phase = 'decay'

            elif self.env_phase == 'decay':
                dur = max(int(self.decay * sr), 1)
                step = (1.0 - self.sustain) / dur
                n = min(dur, remaining)
                env = level - step * np.arange(n)
                env = np.clip(env, self.sustain, 1.0)
                out[i:i+n] = env
                level = env[-1]
                i += n
                if level <= self.sustain:
                    level = self.sustain
                    self.env_phase = 'sustain'

            elif self.env_phase == 'sustain':
                out[i:] = self.sustain
                level = self.sustain
                i = frames
                break

            elif self.env_phase == 'release':
                dur = max(int(self.release * sr), 1)
                step = level / dur
                n = min(dur, remaining)
                env = level - step * np.arange(n)
                env = np.clip(env, 0.0, 1.0)
                out[i:i+n] = env
                level = env[-1]
                i += n
                if level <= 0.001:
                    level = 0.0
                    self.env_phase = 'off'
                    self.active = False

            else:  # 'off'
                out[i:] = 0.0
                i = frames
                break

        self.env_level = level

        for target, param in self.targets:
            target.accept_modulation(param, out)

        return out


class SynthLFO(SynthModulator):
    """
    Low-frequency oscillator for periodic modulation.
    """

    def __init__(self, freq=5.0, depth=1.0, waveform='sine',
                 sample_rate=SAMPLE_RATE):
        super().__init__()
        self.freq = float(freq)
        self.depth = float(depth)
        self.waveform = waveform
        self.sample_rate = sample_rate
        self.phase = 0.0

    def render(self, frames):
        t = np.arange(frames)
        phase_inc = 2 * np.pi * self.freq / self.sample_rate
        phase_array = self.phase + t * phase_inc

        self.phase = (self.phase + frames * phase_inc) % (2 * np.pi)

        if self.waveform == 'sine':
            mod = np.sin(phase_array)
        elif self.waveform == 'square':
            mod = np.sign(np.sin(phase_array))
        elif self.waveform == 'saw':
            mod = 2 * ((phase_array / (2 * np.pi)) % 1) - 1
        elif self.waveform == 'triangle':
            mod = 2 * np.abs(2 * ((phase_array / (2 * np.pi)) % 1) - 1) - 1
        else:
            mod = np.zeros(frames)

        out = self.depth * mod.astype(np.float32)

        for target, param in self.targets:
            target.accept_modulation(param, out)

        return out

