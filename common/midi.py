import time
import threading
import logging
import rtmidi

NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
OCTAVES = range(-2, 9)

midi_note_mapping = {}
for note_idx, note in enumerate(NOTES):
    for octave in OCTAVES:
        if note not in midi_note_mapping:
            midi_note_mapping[note] = {}
        midi_mapping = (octave + 2) * 12 + note_idx
        midi_note_mapping[note][octave] = midi_mapping


class MidiSender:
    def __init__(self, port=0):
        self.logger = logging.getLogger('MidiSender({0})'.format(port))
        self.midiout = rtmidi.MidiOut()
        self.midiout.open_port(port)

    def _note_off(self, midi_num, duration):
        time.sleep(duration)
        self.logger.debug('OFF {0}'.format(midi_num))
        self.midiout.send_message([0x80, midi_num, 0])

    def send_note(self, note, octave, duration):
        self.logger.info('Playing {0}{1} for {2} secs...'.format(note, octave, duration))
        midi_num = midi_note_mapping[note][octave]
        self.logger.debug('ON {0}'.format(midi_num))
        self.midiout.send_message([0x90, midi_num, 112])
        t = threading.Thread(target=self._note_off, args=(midi_num, duration))
        t.start()
