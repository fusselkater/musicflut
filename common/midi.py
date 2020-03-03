import time
from threading import Timer
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


class MidiNote:
    def __init__(self, midiout, note):
        self.logger = logging.getLogger('MidiNote({0})'.format(note))
        self._midiout = midiout
        self._note = note
        self._timer = None

    def _on(self, velocity):
        self.logger.debug('ON')
        self._midiout.send_message([NOTE_ON, self._note, velocity])

    def _off(self):
        self.logger.debug('OFF')
        self._midiout.send_message([NOTE_OFF, self._note, 0])

    def play(self, duration, velocity):
        if self._timer and self._timer.isAlive():
            self._timer.cancel()
        else:
            self._on(velocity)
        self._timer = Timer(duration, self._off)
        self._timer.start()


class MidiSender:
    def __init__(self, port=0):
        self.logger = logging.getLogger('MidiSender({0})'.format(port))
        self._midiout = rtmidi.MidiOut()
        self._midiout.open_port(port)
        self._notes = {}
        for octave in OCTAVES:
            self._notes[octave] = {}
            for note in NOTES:
                midi_mapping = (octave + 2) * 12 + note[1]
                self._notes[octave][note[0]] = MidiNote(self._midiout, midi_mapping)

    def send_note(self, note, octave, duration, velocity):
        try:
            self.logger.info('Note {0}{1} for {2} secs (velocity {3})'.format(note, octave, duration, velocity))
            self._notes[octave][note].play(duration, velocity)
        except KeyError:
            self.logger.info('Note {0}{1} not existend. Ignoring.'.format(note, octave))
