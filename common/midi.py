import time
import threading
import logging
import rtmidi
from rtmidi.midiconstants import NOTE_OFF, NOTE_ON

NOTES = [
    ('C', 0),
    ('C#', 1),
    ('Db', 1),
    ('D', 2),
    ('D#', 3),
    ('Eb', 3),
    ('E', 4),
    ('F', 5),
    ('F#', 6),
    ('Gb', 6),
    ('G', 7),
    ('G#', 8),
    ('Ab', 8),
    ('A', 9),
    ('A#', 10),
    ('Bb', 10),
    ('B', 11)
]
OCTAVES = range(-2, 9)

midi_note_mapping = {}
for note in NOTES:
    for octave in OCTAVES:
        if note[0] not in midi_note_mapping:
            midi_note_mapping[note[0]] = {}
        midi_mapping = (octave + 2) * 12 + note[1]
        midi_note_mapping[note[0]][octave] = midi_mapping


class MidiSender:
    def __init__(self, port=0):
        self.logger = logging.getLogger('MidiSender({0})'.format(port))
        self.midiout = rtmidi.MidiOut()
        self.midiout.open_port(port)

    def _note_off(self, midi_num, duration):
        time.sleep(duration)
        self.logger.debug('OFF {0}'.format(midi_num))
        self.midiout.send_message([NOTE_OFF, midi_num, 0])

    def send_note(self, note, octave, duration, velocity):
        try:
            midi_num = midi_note_mapping[note][octave]
            self.logger.info('Playing {0}{1} for {2} secs...'.format(note, octave, duration))
            self.logger.debug('ON {0}'.format(midi_num))
            self.midiout.send_message([NOTE_ON, midi_num, velocity])
            t = threading.Thread(target=self._note_off, args=(midi_num, duration))
            t.start()
        except KeyError:
            self.logger.info('Note {0}{1} not existend. Ignoring.'.format(note, octave))
