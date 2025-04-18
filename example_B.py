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
    print("Premi 'Z' o 'X' per suonare le voci... (CTRL+C per uscire)")
    try:
        while True:
            time.sleep(0.01)
    except KeyboardInterrupt:
        engine.stop()
        print("Bye!")
