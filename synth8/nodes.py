"""
Audio Signal Modules for Modular Synthesizer.

This module defines audio processing units (Oscillator, Filter, VCA)
used in SynthVoice chains. Each module exposes a unified process()
method and supports modulation via accept_modulation().

Author: Valerio Poggi - 2025
"""

from synth8.engine import SAMPLE_RATE
from synth8.param import ParamRef

import numpy as np
from scipy.signal import butter, sosfilt, sosfilt_zi


class SynthOscillator:
    """
    Basic waveform oscillator: sine, square, sawtooth.
    """

    def __init__(self, freq=440.0, waveform="sine", sample_rate=SAMPLE_RATE):
        """
        Initializes the oscillator.

        Parameters:
            freq (float): Base frequency in Hz.
            waveform (str): Waveform type: 'sine', 'square', 'saw'.
        """
        self.base_freq = freq
        self.waveform = waveform
        self.sample_rate = sample_rate
        self.phase = 0.0
        self._freq_mod = None

    def param(self, name):
        return ParamRef(self, name)

    def accept_modulation(self, param, buffer):
        if param == "freq":
            self._freq_mod = buffer

    def process(self, input, frames):
        """
        Generates a waveform based on frequency and waveform type.

        Parameters:
            input (ignored): Optional input signal (not used).
            frames (int): Number of samples to generate.

        Returns:
            np.ndarray: Generated waveform block.
        """
        t = np.arange(frames)

        # Combine base frequency with modulation, if any
        if self._freq_mod is not None:
            freq = self.base_freq + self._freq_mod[:frames]
        else:
            freq = self.base_freq

        # Ensure freq is a valid array and clip to safe bounds
        if isinstance(freq, np.ndarray):
            freq = np.clip(freq, 20.0, 20000.0)
            phase_inc = 2 * np.pi * freq / self.sample_rate
        else:
            freq = np.clip(freq, 20.0, 20000.0)
            phase_inc = 2 * np.pi * freq / self.sample_rate
            phase_inc = np.full(frames, phase_inc)

        # Advance phase and generate waveform
        phase_array = self.phase + np.cumsum(phase_inc)
        self.phase = phase_array[-1] % (2 * np.pi)

        if self.waveform == "sine":
            signal = np.sin(phase_array)
        elif self.waveform == "square":
            signal = np.sign(np.sin(phase_array))
        elif self.waveform == "saw":
            signal = 2 * ((phase_array / (2 * np.pi)) % 1) - 1
        else:
            signal = np.zeros(frames, dtype=np.float32)

        return signal.astype(np.float32)



class SynthFilter:
    """
    Simple 2nd-order lowpass filter.
    """

    def __init__(self, cutoff=1000.0, sample_rate=SAMPLE_RATE):
        """
        Initializes the filter.

        Parameters:
            cutoff (float): Cutoff frequency in Hz.
        """
        self.base_cutoff = cutoff
        self.sample_rate = SAMPLE_RATE
        self._cutoff_mod = None
        self._sos = None
        self._zi = None
        self._last_cutoff = None

    def param(self, name):
        return ParamRef(self, name)

    def accept_modulation(self, param, buffer):
        if param == "cutoff":
            self._cutoff_mod = buffer

    def _design_filter(self, cutoff):
        wn = cutoff / (0.5 * self.sample_rate)
        sos = butter(N=2, Wn=wn, btype="low", output="sos")
        zi = sosfilt_zi(sos)
        return sos, zi

    def process(self, input, frames):
        """
        Applies lowpass filtering.

        Parameters:
            input (np.ndarray): Input audio.
            frames (int): Number of samples.

        Returns:
            np.ndarray: Filtered signal.
        """
        if input is None:
            return np.zeros(frames, dtype=np.float32)

        if self._cutoff_mod is not None:
            # Use first value to design static filter
            cutoff = float(np.clip(self._cutoff_mod[0], 50, 20000))
        else:
            cutoff = self.base_cutoff

        if self._sos is None or cutoff != self._last_cutoff:
            self._sos, self._zi = self._design_filter(cutoff)
            self._last_cutoff = cutoff

        output, self._zi = sosfilt(self._sos, input, zi=self._zi)
        return output.astype(np.float32)


class SynthVCA:
    """
    Voltage-controlled amplifier. Controls amplitude via gain.
    """

    def __init__(self, gain=1.0):
        """
        Initializes the VCA.

        Parameters:
            gain (float): Static gain value.
        """
        self.base_gain = gain
        self._gain_mod = None

    def param(self, name):
        return ParamRef(self, name)

    def accept_modulation(self, param, buffer):
        if param == "gain":
            self._gain_mod = buffer

    def process(self, input, frames):
        """
        Scales the input by a gain factor.

        Parameters:
            input (np.ndarray): Audio signal.
            frames (int): Number of samples.

        Returns:
            np.ndarray: Amplitude-modulated signal.
        """
        if input is None:
            return np.zeros(frames, dtype=np.float32)

        if self._gain_mod is not None:
            gain = self._gain_mod[:frames]
        else:
            gain = self.base_gain

        if isinstance(gain, np.ndarray):
            return input * gain
        else:
            return input * float(gain)

