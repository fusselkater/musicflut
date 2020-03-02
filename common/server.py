import socket
from threading import Thread
from common.midi import MidiSender
import logging


class MusicThread(Thread):
    def __init__(self, midisender, conn, host, port):
        Thread.__init__(self)
        self.logger = logging.getLogger('MusicThread({0}:{1})'.format(host, port))
        self.midisender = midisender
        self.conn = conn
        self.host = host
        self.port = port

    def run(self):
        buffer = bytearray()
        while self.is_alive():
            chunk = self.conn.recv(100)
            if not chunk:
                break
            buffer.extend(chunk)
            while b'\n' in buffer:
                line = buffer[:buffer.find(b'\n')].decode('ascii')
                self.logger.debug('recv line: ' + line)
                buffer = buffer[buffer.find(b'\n') + 1:]
                columns = line.split(' ')
                self.parse_command(columns[0], columns[1:])
        self.stop()

    def parse_command(self, command, argv):
        try:
            command_method = getattr(self, 'cmd_' + command.lower())
            command_method(argv)
        except AttributeError:
            self.conn.send('Invalid command\n'.encode('ascii'))

    def cmd_play(self, argv):
        self.midisender.send_note(argv[0], int(argv[1]), float(argv[2]))

    def stop(self):
        self.conn.shutdown(socket.SHUT_RDWR)


class MusicServer:
    def __init__(self, family=socket.AF_INET, host='127.0.0.1', port='1234'):
        self.logger = logging.getLogger('MusicServer({0}:{1})'.format(host, port))
        self.socket = socket.socket(family, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.midisender = MidiSender()
        self.socket.bind((host, port))
        self.threads = []

    def serve(self):
        while True:
            self.logger.info('Listening for new connection...')
            self.socket.listen(4)
            try:
                (conn, (host, port)) = self.socket.accept()
            except OSError:
                break
            self.logger.info('Accepted connection from {0}:{1}.'.format(host, port))
            newthread = MusicThread(self.midisender, conn, host, port)
            newthread.start()
            self.threads.append(newthread)

        for thread in self.threads:
            thread.stop()
            thread.join()

    def stop(self):
        self.logger.info('Stopping server...')
        self.socket.shutdown(socket.SHUT_RDWR)
