import socket
import select
import time
import re
import logging

LOGGER = logging.getLogger(__name__)

class Player(object):
    _boolean = {"True": True, "False": False}

    def __init__(self, bytestring):
        try:
            self._player = dict(re.findall(b"(\w+)=([\w\d.]+)", bytestring))
            self._player.update(re.match(b"^.*id=[0-9]+,\s*(?P<name>.*),\s*pos=\((?P<pos>[^)]+)\),\s*rot=\((?P<rot>[^)]+)\)", bytestring).groupdict())
            self._player[b"id"]
            self._player["name"]
        except (KeyError, AttributeError):
            raise ValueError

    def __str__(self):
        return str(self._player)

    def _int(self, key):
        if key not in self._player:
            return None
        return int(self._player[key])

    @property
    def pos(self):
        try:
            return tuple(map(float,self._player["pos"].split(b",")))
        except (ValueError, KeyError):
            return (None, None, None)

    @property
    def rot(self):
        try:
            return tuple(map(float,self._player["rot"].split(b",")))
        except (ValueError, KeyError):
            return (None, None, None)

    @property
    def name(self):
        if "name" not in self._player:
            None
        return self._player["name"].decode('utf-8')

    @property
    def ip(self):
        if b"ip" not in self._player:
            None
        return self._player[b"ip"].decode('latin1')

    @property
    def id(self):
        return self._int(b"id")

    @property
    def remote(self):
        return self._int(b"remote")

    @property
    def health(self):
        return self._int(b"health")

    @property
    def deaths(self):
        return self._int(b"deaths")

    @property
    def zombies(self):
        return self._int(b"zombies")

    @property
    def players(self):
        return self._int(b"players")

    @property
    def score(self):
        return self._int(b"score")

    @property
    def level(self):
        return self._int(b"level")

    @property
    def steamid(self):
        return self._int(b"steamid")

    @property
    def ping(self):
        return self._int(b"ping")

class Telnet(object):
    boolean = {True: 'true', False: 'false'}
    _pattern_type = type(re.compile(""))
    _re_flags = re.IGNORECASE|re.DOTALL|re.MULTILINE

    def __init__(self, host='127.0.0.1', port=8081):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(60)
        self.address = (host, port)
        self._buffer = b''
        self._listen = False

    def connect(self):
        self._buffer = b''
        LOGGER.debug("Connecting to {0}:{1}".format(self.address[0], self.address[1]))
        self.sock.connect(self.address)
        LOGGER.info("Connected to {0}:{1}".format(*self.sock.getpeername()))
        response = self.receive(re.compile(b'^(\*\*\*\s*Connected.*to end session.)\r\n\r\n', self._re_flags))
        if response:
            messages = dict(re.findall(b'^([\w ]+):\s*([^\r\n]*)', b''.join(response.groups()), self._re_flags))
            for key, value in messages.items():
                LOGGER.info("{0}: [{1}]".format(key, value))
        else:
            LOGGER.error("Failed to parse welcome message")
        if not self.loglevel(enabled=False):
            LOGGER.critical("Failed to disable logging")
            self.disconnect()
            return False
        return True

    def receive(self, regex, timeout=60):
        assert type(regex) is self._pattern_type, "'regex' is not a compiled regular expression pattern"
        assert not self._listen, 'not possible to read while listening'
        m = regex.search(self._buffer)
        t = time.time()
        try:
            while not m:
                to = max(0, timeout-(time.time()-t))
                (rl, wl, xl) = select.select([self.sock], [], [], to)
                try:
                    data = rl[0].recv(2048)
                    LOGGER.debug("recv: {0}".format(data))
                    if len(data) == 0:
                        raise EOFError
                    self._buffer += data
                    m = regex.search(self._buffer)
                except IndexError:
                    raise socket.timeout
            self._buffer = self._buffer[m.end():]
            return m
        except socket.timeout:
            LOGGER.warn("Socket timeout, flushing read-buffer: {0}".format(self._buffer))
            self._buffer = b''
            return None

    def gettime(self):
        try:
            t = self.command("gettime", 
                             re.compile(b'^day\s+(?P<day>[0-9]+),\s+(?P<hour>[0-9]+):(?P<minute>[0-9]+)\s*\r\n', self._re_flags)).groupdict()
            for key, value in t.items():
                t[key] = int(t[key])
            return time.struct_time((
                       int(t['day']/365),
                       int(t['day']/30)%12,
                       t['day']%30,
                       t['hour'],
                       t['minute'],
                       0,
                       t['day']%7-1,
                       t['day']%365,
                       0))
        except (AttributeError, ValueError):
            return None

    def listplayers(self):
        LOGGER.info("Listing players")
        self.sock.sendall(b".\r\nlistplayers\r\n")
        regex = re.compile(b"'.'\r\n(.*)Total of ([0-9]+) in the game", self._re_flags)
        response = self.receive(regex)
        players = []
        for line in response.group(1).split(b"\r\n"):
            try:
                player = Player(line)
                players.append(player)
            except ValueError:
                pass
        if int(response.group(2)) != len(players):
            LOGGER.warn("Reported player amount did not match parsed players ({0} vs {1})".format(int(response.group(2)), len(players)))
        return players

    def listents(self):
        return self.command("listents",
                            re.compile(b"(^.*in the game)\r\n", self._re_flags))

    def getgamepref(self):
        return self.command("getgamepref")

    def version(self):
        response = b"".join(self.command("version").groups())
        try:
            version = re.search(b"^game version: (?P<version>.*) compatibility Version: (?P<compatibility>[^\r\n]*)\r\n",
                                response, self._re_flags).groupdict()
            version['mods'] = re.findall(b"^mod\s*([^\r\n]*)\r\n", response, self._re_flags)
            return version
        except AttributeError:
            return None

    def loglevel(self, level='ALL', enabled=True):
        LOGGER.info("Setting loglevel '{0}' to '{1}'".format(level, enabled))
        request = "loglevel {0} {1}\r\n".format(level, self.boolean[enabled])
        self.sock.sendall(request.encode("ascii"))
        return self.receive(re.compile(b"^([disaen]+bling[^\r\n]*)\r\n", self._re_flags))

    def say(self, message):
        return self.sock.sendall('say "{0}"\r\n'.format(message).encode("ascii"))
        #return self.command('say "{0}"'.format(message))

    def command(self, cmd):
        LOGGER.info("Executing command: '{0}'".format(cmd))
        self.sock.sendall(cmd.encode("ascii") + b"\r\n.\r\n")
        regex = re.compile(b"(.*)\*\*\* ERROR: unknown command '.'\r\n", self._re_flags)
        return b''.join(self.receive(regex).groups()).decode('utf-8')

    @property
    def connected(self):
        try:
            self.sock.getpeername()
            return True
        except OSError:
            return False

    def disconnect(self):
        if self.connected:
            LOGGER.debug("disconnecting from {0}:{1}".format(*self.sock.getpeername()))
            self.sock.sendall(b'exit\r\n')
            self.sock.close()
            LOGGER.info("disconnected from {0}:{1}".format(self.address[0], self.address[1]))
        return True

    def __del__(self):
        self.disconnect()

    def __iter__(self):
        self.sock.settimeout(None)
        return self

    def __next__(self):
        m = self._buffer.find(b'\n')
        while m < 0:
            data = self.sock.recv(2048)
            LOGGER.debug("recv: {0}".format(data))
            if len(data) == 0:
                raise EOFError
            self._buffer += data
            m = self._buffer.find(b'\n')
        (row, self._buffer) = (self._buffer[:(m+1)], self._buffer[(m+1):])
        return row
