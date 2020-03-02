#!/usr/bin/env python3

import logging
import signal
from common.server import MusicServer


def signal_handler(signum, frame):
    server.stop()


logging.basicConfig(level=logging.DEBUG)
logging.info('Starting musicflut server...')
server = MusicServer(host='0.0.0.0', port=1234, midi_port=0)
signal.signal(signal.SIGINT, signal_handler)
server.serve()
