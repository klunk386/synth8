"""
Real-Time Audio Engine for Modular Synthesizer Voices.

This module defines the SynthEngine class, which manages real-time audio
playback and maps keyboard events to user-defined synthesizer voices.

Author: Valerio Poggi - 2025
"""

from synth8.terminal import TerminalSilent

import time
import threading
import numpy as np
import sounddevice as sd
from pynput import keyboard


SAMPLE_RATE = 44100
BLOCK_SIZE = 512
LATENCY = 0.01


class SynthEngine:
    """
    Real-time audio engine that handles SynthVoice instances and
    keyboard input for triggering.
    """

    def __init__(self):
        """
        Initializes the SynthEngine with no voices or modulators.
        """
        self.voices = {}
        self.modulators = []
        self.keymap = {}
        self._pressed_keys = set()
        self._lock = threading.Lock()
        self.stream = None
        self.listener = None

    def add_voice(self, voice, id, key=None):
        """
        Registers a SynthVoice instance with an optional keyboard key.

        Parameters:
            voice (SynthVoice): The voice to add.
            id (str): Unique identifier.
            key (str, optional): Keyboard character to trigger the voice.
        """
        with self._lock:
            self.voices[id] = voice
            if key:
                self.keymap[key.lower()] = id

    def remove_voice(self, id):
        """
        Removes a voice and its key mapping.

        Parameters:
            id (str): Identifier of the voice to remove.
        """
        with self._lock:
            for key, val in list(self.keymap.items()):
                if val == id:
                    del self.keymap[key]
            if id in self.voices:
                del self.voices[id]

    def voice_on(self, id):
        """
        Triggers a voice to begin its attack phase.

        Parameters:
            id (str): Voice identifier.
        """
        with self._lock:
            if id in self.voices:
                self.voices[id].trigger_on()

    def voice_off(self, id):
        """
        Triggers the release phase of a voice.

        Parameters:
            id (str): Voice identifier.
        """
        with self._lock:
            if id in self.voices:
                self.voices[id].trigger_off()

    def _on_press(self, key):
        try:
            char = key.char.lower()
            if char in self.keymap and char not in self._pressed_keys:
                self._pressed_keys.add(char)
                self.voice_on(self.keymap[char])
        except AttributeError:
            pass

    def _on_release(self, key):
        try:
            char = key.char.lower()
            if char in self._pressed_keys:
                self._pressed_keys.remove(char)
                self.voice_off(self.keymap[char])
        except AttributeError:
            pass

    def _callback(self, outdata, frames, time_info, status):
        """
        Real-time audio callback function.

        Parameters:
            outdata (np.ndarray): Audio output buffer.
            frames (int): Number of samples to generate.
            time_info (dict): Timing metadata.
            status (CallbackFlags): Stream status flags.
        """
        mix = np.zeros(frames, dtype=np.float32)

        with self._lock:
            active = 0
            for voice in self.voices.values():
                if voice.active:
                    signal = voice.render(frames)
                    if signal is not None:
                        mix += signal
                        active += 1

            if active > 0:
                mix *= 1.0 / np.sqrt(active)

        # Output stereo (dual-mono)
        outdata[:] = np.column_stack((mix, mix))

    def _start_keyboard_listener(self):
        """
        Starts a keyboard listener for triggering voices.
        """
        self.listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release
        )
        self.listener.start()

    def play(self, wait=False):
        """
        Starts audio playback and keyboard listener.

        Parameters:
            wait (bool): If True, block execution until Ctrl+C is pressed.
        """
        self._start_keyboard_listener()
        self.stream = sd.OutputStream(
            samplerate=SAMPLE_RATE,
            blocksize=BLOCK_SIZE,
            channels=2,
            callback=self._callback,
            latency=LATENCY
        )
        self.stream.start()

        if wait:
            print("Press key to play. Press Ctrl+C to stop.")
            try:
                with TerminalSilent():
                    while True:
                        time.sleep(0.01)
            except KeyboardInterrupt:
                self.stop()
                print("Stopped.")

    def stop(self):
        """
        Stops audio playback and the keyboard listener.
        """
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
        if self.listener:
            self.listener.stop()
            self.listener = None

