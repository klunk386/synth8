"""
SynthVoice and Mixer for Modular Synthesizer Architecture.

SynthVoice represents a signal chain of audio processing nodes (oscillators,
filters, amplifiers, etc.) that can be triggered and rendered. Mixer allows
combining multiple voices into a polyphonic or layered output.

Author: Valerio Poggi - 2025
"""

import numpy as np
import threading


class SynthVoice:
    """
    Represents a monophonic voice composed of connected audio modules
    and associated modulators. Supports both gated and ungated playback.
    """

    def __init__(self):
        """
        Initializes an empty voice.
        """
        self.modules = []
        self.modulators = []
        self.active = False
        self.gate_on = False

    def connect(self, module):
        """
        Adds an audio module (or a list of modules) to the voice chain.

        Parameters:
            module (SynthNode or list): Node(s) to connect.
        """
        if isinstance(module, list):
            self.modules.extend(module)
        else:
            self.modules.append(module)

    def modulate(self, modulator, target, param=None):
        """
        Connects a modulator to a parameter.

        Parameters:
            modulator (SynthModulator): The modulation source.
            target (object or ParamRef): Target of modulation.
            param (str, optional): Parameter name (if not using ParamRef).
        """
        self.modulators.append(modulator)
        if param is None and hasattr(target, "module") and hasattr(target, "name"):
            modulator.modulate(target.module, target.name)
        else:
            modulator.modulate(target, param)

    def add_modulator(self, modulator):
        """
        Registers one or more modulators.

        Parameters:
            modulator (SynthModulator or list): Modulator(s) to add.
        """
        if isinstance(modulator, list):
            self.modulators.extend(modulator)
        else:
            self.modulators.append(modulator)

    def trigger_on(self):
        """
        Starts the envelope and marks the voice as active.
        """
        self.gate_on = True
        for mod in self.modulators:
            if hasattr(mod, "trigger_on"):
                mod.trigger_on()
        self.active = True

    def trigger_off(self):
        """
        Starts the release phase and marks the gate as off.
        """
        self.gate_on = False
        for mod in self.modulators:
            if hasattr(mod, "trigger_off"):
                mod.trigger_off()

    def render(self, frames):
        """
        Processes modulation and audio for this voice.

        Parameters:
            frames (int): Number of samples to render.

        Returns:
            np.ndarray: Output signal block.
        """
        for mod in self.modulators:
            mod.render(frames)

        signal = None
        for module in self.modules:
            signal = module.process(signal, frames)

        any_mod_active = any(
            getattr(mod, "active", False) for mod in self.modulators
        )

        # Deactivate when key is released and all modulators are inactive
        if not self.gate_on and not any_mod_active:
            self.active = False
        else:
            self.active = True

        return signal if signal is not None else np.zeros(frames, dtype=np.float32)


class Mixer:
    """
    Combines multiple SynthVoice instances into a single audio output stream.
    Automatically removes voices that are no longer active.
    """

    def __init__(self, voices=None, gain=1.0):
        """
        Initializes the mixer.

        Parameters:
            voices (list of SynthVoice, optional): Voices to mix.
            gain (float): Output gain factor.
        """
        self.voices = voices if voices else []
        self.gain = gain
        self._lock = threading.Lock()

    def add_voice(self, voice):
        """
        Adds a SynthVoice to the mixer.

        Parameters:
            voice (SynthVoice): Voice to add.
        """
        with self._lock:
            self.voices.append(voice)

    def remove_voice(self, voice):
        """
        Removes a SynthVoice from the mixer.

        Parameters:
            voice (SynthVoice): Voice to remove.
        """
        with self._lock:
            if voice in self.voices:
                self.voices.remove(voice)

    def trigger_on(self):
        """
        Triggers all voices in the mixer.
        """
        with self._lock:
            for voice in self.voices:
                voice.trigger_on()

    def trigger_off(self):
        """
        Triggers release phase for all voices.
        """
        with self._lock:
            for voice in self.voices:
                voice.trigger_off()

    @property
    def active(self):
        """
        Returns True if at least one voice is active.
        """
        with self._lock:
            return any(v.active for v in self.voices)

    def render(self, frames):
        """
        Renders audio from all voices, removes inactive ones,
        and mixes the active ones.

        Parameters:
            frames (int): Number of samples.

        Returns:
            np.ndarray: Mixed output signal.
        """
        mix = np.zeros(frames, dtype=np.float32)
        active_count = 0

        with self._lock:
            surviving = []

            for voice in self.voices:
                signal = voice.render(frames)
                if voice.active and signal is not None:
                    mix += signal
                    active_count += 1
                    surviving.append(voice)

            # Replace with only still-active voices
            self.voices = surviving

        if active_count > 0:
            mix *= self.gain / active_count

        return mix


