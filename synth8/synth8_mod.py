
# (HEADER E IMPORT INVARIATI)
import sys
import os
import numpy as np
import sounddevice as sd
from scipy.signal import butter, sosfilt, sosfilt_zi
from pynput import keyboard
import threading

SAMPLE_RATE = 44100
BLOCK_SIZE = 1024

# (SynthVoice, Mixer: INVARIATI)

class SynthEngine:
    def __init__(self):
        self.voices = {}
        self.keymap = {}
        self.stream = None
        self.listener = None
        self._pressed_keys = set()
        self._lock = threading.Lock()

    def add_voice(self, voice, id, key=None):
        with self._lock:
            self.voices[id] = voice
            if key:
                self.keymap[key.lower()] = id

    def remove_voice(self, id):
        with self._lock:
            for key, val in list(self.keymap.items()):
                if val == id:
                    del self.keymap[key]
            if id in self.voices:
                del self.voices[id]

    def voice_on(self, id):
        with self._lock:
            if id in self.voices:
                self.voices[id].trigger_on()

    def voice_off(self, id):
        with self._lock:
            if id in self.voices:
                self.voices[id].trigger_off()

    def _on_press(self, key):
        try:
            char = key.char.lower()
            with self._lock:
                if char in self.keymap and char not in self._pressed_keys:
                    self._pressed_keys.add(char)
                    self.voice_on(self.keymap[char])
        except AttributeError:
            pass

    def _on_release(self, key):
        try:
            char = key.char.lower()
            with self._lock:
                if char in self._pressed_keys:
                    self._pressed_keys.remove(char)
                    self.voice_off(self.keymap[char])
        except AttributeError:
            pass

    def _callback(self, outdata, frames, time_info, status):
        mix = np.zeros(frames, dtype=np.float32)
        with self._lock:
            voices_copy = list(self.voices.values())
        for voice in voices_copy:
            mix += voice.render(frames)
        active_count = max(1, len([v for v in voices_copy if v.active]))
        outdata[:] = (mix / active_count).reshape(-1, 1)

    def _start_keyboard_listener(self):
        self.listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release
        )
        self.listener.start()

    def play(self):
        self._start_keyboard_listener()
        self.stream = sd.OutputStream(
            samplerate=SAMPLE_RATE,
            blocksize=BLOCK_SIZE,
            channels=1,
            callback=self._callback,
            latency='low'
        )
        self.stream.start()

    def stop(self):
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
        if self.listener:
            self.listener.stop()
            self.listener = None
