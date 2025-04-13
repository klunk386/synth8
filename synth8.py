"""
Synth Engine and Voice System for Real-Time Audio Synthesis in Python.

This module provides a modular synthesizer framework where each SynthVoice
can be triggered by a specific keyboard key. It includes basic waveform
oscillators, lowpass filtering, ADSR envelope shaping, and LFO modulation.

Compatible with Linux, macOS, and Windows (limited terminal control).

Author: Valerio Poggi - 2025
"""

import sys
import os
import numpy as np
import sounddevice as sd
from scipy.signal import butter, lfilter
from pynput import keyboard

SAMPLE_RATE = 44100
BLOCK_SIZE = 512


class TerminalSilent:
    """
    Context manager to disable terminal input echo across platforms.

    On Unix systems (Linux/macOS), this sets the terminal to non-canonical
    mode to avoid echoing characters typed during runtime. On Windows, echo
    is not disabled but no blocking occurs. This is mainly useful for
    keyboard-controlled synthesizer interaction via terminal.
    """
    def __enter__(self):
        """
        Enters the silent terminal context. On Unix, applies raw mode
        to stdin. On Windows, imports msvcrt but performs no changes.
        """
        self.platform = sys.platform
        if self.platform.startswith('linux') or self.platform == 'darwin':
            import termios
            import tty
            self.fd = sys.stdin.fileno()
            self.old_settings = termios.tcgetattr(self.fd)
            tty.setcbreak(self.fd)
            self.termios = termios
        elif self.platform == 'win32':
            import msvcrt
            self.msvcrt = msvcrt
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Exits the silent terminal context, restoring original terminal
        settings (Unix only).
        """
        if self.platform.startswith('linux') or self.platform == 'darwin':
            self.termios.tcsetattr(self.fd, self.termios.TCSADRAIN,
                                   self.old_settings)


class SynthVoice:
    """
    Represents a single synthesizer voice.

    Each voice has an oscillator (sine, square, or saw), optional lowpass
    filtering, an ADSR envelope, and an LFO for frequency modulation.
    """

    def __init__(self):
        """
        Initializes default oscillator, ADSR, and LFO parameters.
        """
        self.freq = 440
        self.waveform = 'sine'
        self.cutoff = None
        self.phase = 0

        self.lfo_enabled = False
        self.lfo_freq = 5.0
        self.lfo_depth = 5.0
        self.lfo_waveform = 'sine'
        self.lfo_phase = 0

        self.adsr_params = {
            'attack': 0.01,
            'decay': 0.1,
            'sustain': 0.7,
            'release': 0.3
        }

        self.env_phase = 'off'
        self.env_level = 0.0
        self.active = False

    def oscillator(self, freq=440, waveform='sine'):
        """
        Sets the oscillator's base frequency and waveform.

        Parameters:
            freq (float): Frequency in Hz.
            waveform (str): Type of waveform ('sine', 'saw', 'square').
        """
        self.freq = freq
        self.waveform = waveform

    def lowpass(self, cutoff=1000):
        """
        Sets the cutoff frequency for a simple lowpass filter.

        Parameters:
            cutoff (float): Filter cutoff in Hz.
        """
        self.cutoff = cutoff

    def adsr(self, attack=0.01, decay=0.1, sustain=0.7, release=0.3):
        """
        Sets the ADSR envelope parameters.

        Parameters:
            attack (float): Time to reach full amplitude (seconds).
            decay (float): Time to fall to sustain level (seconds).
            sustain (float): Amplitude level during sustain (0 to 1).
            release (float): Time to fade out after key release (seconds).
        """
        self.adsr_params = {
            'attack': attack,
            'decay': decay,
            'sustain': sustain,
            'release': release
        }

    def lfo(self, freq=5.0, depth=5.0, waveform='sine'):
        """
        Enables an LFO for modulating oscillator frequency.

        Parameters:
            freq (float): Frequency of LFO in Hz.
            depth (float): Modulation depth in Hz.
            waveform (str): LFO waveform ('sine', 'square', 'saw', 'triangle').
        """
        self.lfo_enabled = True
        self.lfo_freq = freq
        self.lfo_depth = depth
        self.lfo_waveform = waveform
        self.lfo_phase = 0

    def _generate_lfo(self, frames):
        t = (np.arange(frames) + self.lfo_phase) / SAMPLE_RATE
        self.lfo_phase += frames

        if self.lfo_waveform == 'sine':
            mod = np.sin(2 * np.pi * self.lfo_freq * t)
        elif self.lfo_waveform == 'square':
            mod = np.sign(np.sin(2 * np.pi * self.lfo_freq * t))
        elif self.lfo_waveform == 'saw':
            mod = 2 * (t * self.lfo_freq - np.floor(0.5 + t * self.lfo_freq))
        elif self.lfo_waveform == 'triangle':
            mod = 2 * np.abs(2 * (t * self.lfo_freq % 1) - 1) - 1
        else:
            mod = np.zeros(frames)

        return mod.astype(np.float32)

    def _generate_waveform(self, frames):
        base_freq = self.freq
        if self.lfo_enabled:
            mod_signal = self._generate_lfo(frames)
            freq_mod = base_freq + self.lfo_depth * mod_signal
        else:
            freq_mod = np.full(frames, base_freq)

        t = (np.arange(frames) + self.phase) / SAMPLE_RATE
        self.phase += frames

        wave = np.sin(2 * np.pi * freq_mod * t)
        if self.waveform == 'saw':
            wave = 2 * (t * freq_mod - np.floor(0.5 + t * freq_mod))
        elif self.waveform == 'square':
            wave = np.sign(np.sin(2 * np.pi * freq_mod * t))

        return wave.astype(np.float32)

    def _apply_filter(self, signal):
        if self.cutoff:
            b, a = butter(2, self.cutoff / (0.5 * SAMPLE_RATE), btype='low')
            return lfilter(b, a, signal).astype(np.float32)
        return signal

    def _generate_envelope(self, frames):
        out = np.zeros(frames, dtype=np.float32)
        for i in range(frames):
            if self.env_phase == 'attack':
                self.env_level += (1.0 /
                    (self.adsr_params['attack'] * SAMPLE_RATE))
                if self.env_level >= 1.0:
                    self.env_level = 1.0
                    self.env_phase = 'decay'
            elif self.env_phase == 'decay':
                self.env_level -= (
                    (1.0 - self.adsr_params['sustain']) /
                    (self.adsr_params['decay'] * SAMPLE_RATE)
                )
                if self.env_level <= self.adsr_params['sustain']:
                    self.env_level = self.adsr_params['sustain']
                    self.env_phase = 'sustain'
            elif self.env_phase == 'sustain':
                self.env_level = self.adsr_params['sustain']
            elif self.env_phase == 'release':
                self.env_level -= (
                    self.adsr_params['sustain'] /
                    (self.adsr_params['release'] * SAMPLE_RATE)
                )
                if self.env_level <= 0:
                    self.env_level = 0
                    self.env_phase = 'off'
                    self.active = False
            elif self.env_phase == 'off':
                self.env_level = 0
            out[i] = self.env_level
        return out

    def render(self, frames):
        """
        Generates the audio samples for this voice.

        Parameters:
            frames (int): Number of audio samples to generate.

        Returns:
            np.ndarray: Audio signal as 1D float32 array.
        """
        if not self.active and self.env_phase == 'off':
            return np.zeros(frames, dtype=np.float32)

        wave = self._generate_waveform(frames)
        env = self._generate_envelope(frames)
        shaped = wave * env
        return self._apply_filter(shaped)

    def trigger_on(self):
        """
        Triggers the start of the ADSR envelope (attack phase),
        and resets oscillator and LFO phases.
        """
        self.phase = 0
        self.lfo_phase = 0
        self.env_phase = 'attack'
        self.env_level = 0.0
        self.active = True

    def trigger_off(self):
        """
        Triggers the release phase of the envelope,
        allowing the voice to fade out naturally.
        """
        if self.active:
            self.env_phase = 'release'


class SynthEngine:
    """
    SynthEngine manages multiple SynthVoice instances and maps them
    to keyboard keys for live triggering. Handles real-time audio
    playback and keyboard event listening.

    Attributes:
        voices (dict): Mapping from IDs to SynthVoice instances.
        keymap (dict): Mapping from keys to voice IDs.
        stream (OutputStream): Audio stream used for audio playback.
        listener (Listener): Keyboard event listener (pynput).
        _pressed_keys (set): Tracks currently pressed keys to avoid repeats.
    """

    def __init__(self):
        """
        Initializes the SynthEngine with empty voice and key mappings,
        and prepares for audio and keyboard interaction.
        """
        self.voices = {}
        self.keymap = {}
        self.stream = None
        self.listener = None
        self._pressed_keys = set()

    def add_voice(self, voice, id, key=None):
        """
        Adds a SynthVoice to the engine and optionally maps it to a key.

        Args:
            voice (SynthVoice): The voice instance to register.
            id (str): Unique identifier for the voice.
            key (str, optional): Lowercase keyboard character to trigger it.
        """
        self.voices[id] = voice
        if key:
            self.keymap[key.lower()] = id

    def remove_voice(self, id):
        """
        Removes a voice and its associated key mapping, if any.

        Args:
            id (str): Identifier of the voice to remove.
        """
        for key, val in list(self.keymap.items()):
            if val == id:
                del self.keymap[key]
        if id in self.voices:
            del self.voices[id]

    def voice_on(self, id):
        """
        Triggers a voice by ID (starts its attack phase).

        Args:
            id (str): Identifier of the voice to trigger.
        """
        if id in self.voices:
            self.voices[id].trigger_on()

    def voice_off(self, id):
        """
        Releases a voice by ID (starts its release phase).

        Args:
            id (str): Identifier of the voice to release.
        """
        if id in self.voices:
            self.voices[id].trigger_off()

    def _on_press(self, key):
        """
        Internal method to handle key press events. Triggers a voice
        if the key is mapped and was not already pressed.

        Args:
            key (Key): pynput Key event object.
        """
        try:
            char = key.char.lower()
            if char in self.keymap:
                if char not in self._pressed_keys:
                    self._pressed_keys.add(char)
                    self.voice_on(self.keymap[char])
        except AttributeError:
            pass

    def _on_release(self, key):
        """
        Internal method to handle key release events. Ends a voice's
        envelope if the key was previously pressed.

        Args:
            key (Key): pynput Key event object.
        """
        try:
            char = key.char.lower()
            if char in self._pressed_keys:
                self._pressed_keys.remove(char)
                self.voice_off(self.keymap[char])
        except AttributeError:
            pass

    def _callback(self, outdata, frames, time_info, status):
        """
        Audio callback used by sounddevice to stream real-time audio.

        Args:
            outdata (ndarray): Output audio buffer to fill.
            frames (int): Number of audio frames to generate.
            time_info (dict): Timing metadata (unused).
            status (CallbackFlags): Stream status flags.
        """
        mix = np.zeros(frames, dtype=np.float32)
        for voice in self.voices.values():
            mix += voice.render(frames)
        active_count = max(1, len([v for v in self.voices.values() if v.active]))
        outdata[:] = (mix / active_count).reshape(-1, 1)

    def _start_keyboard_listener(self):
        """
        Starts the pynput keyboard listener for press and release events.
        """
        self.listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release
        )
        self.listener.start()

    def play(self):
        """
        Starts the audio stream and keyboard listener.
        """
        self._start_keyboard_listener()
        self.stream = sd.OutputStream(
            samplerate=SAMPLE_RATE,
            blocksize=BLOCK_SIZE,
            channels=1,
            callback=self._callback
        )
        self.stream.start()

    def stop(self):
        """
        Stops and closes the audio stream and keyboard listener.
        """
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
        if self.listener:
            self.listener.stop()
            self.listener = None

