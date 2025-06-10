"""
Synth8: Modular Audio Synthesis Engine

Exposes top-level components for engine control, signal generation,
modulation, and voice routing.
"""

# Core engine and voice
from .engine import SynthEngine
from .voice import SynthVoice, Mixer

# Signal processing nodes
from .nodes import SynthOscillator, SynthFilter, SynthVCA

# Modulators
from .modulators import SynthADSR, SynthLFO

from .param import ParamRef
from .terminal import TerminalSilent
