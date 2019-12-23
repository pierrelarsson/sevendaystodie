import socket
import select
import time
import re
import logging
from datetime import datetime

LOGGER = logging.getLogger(__name__)

re_event = re.compile(r"^(?P<date>[0-9-]*)T(?P<time>[0-9:]*)\s+(?P<uptime>[0-9.]*)\s+(?P<loglevel>[A-Z]*)\s+(?P<message>.*)")
re_chat = re.compile(r"^Chat\s+\(from '(?P<from>[^']*)', entity id '(?P<entity>[^']*)', to '(?P<to>[^']*)'\): (?P<message>.*)")
re_gmsg = re.compile(r"^GMSG:\s*(?P<message>.*)")
re_status = re.compile(r"^Time: (?P<time>[0-9.hms]+) FPS: (?P<fps>[0-9.]+) Heap: (?P<heap>[0-9.tgmb]+) Max: (?P<max>[0-9.tgmb]+) Chunks: (?P<chunks>[0-9]+) CGO: (?P<cgo>[0-9]+) Ply: (?P<players>[0-9]+) Zom: (?P<zombies>[0-9]+) Ent: (?P<enteties>[0-9() ]+) Items: (?P<items>[0-9]+) CO: (?P<co>[0-9]+) RSS: (?P<rss>[0-9.tgmb]+)", re.IGNORECASE)
re_entity = re.compile(r"^Entity (?P<entity>\S+) (?P<entityid>[0-9]+) (?P<event>\S+)\s*(?P<reason>.*)")


#Heap: (?P<heap>[0-9.tgmb]+) Max: (?P<max>[0-9.tgmb]+) Chunks: (?<chunks>[0-9]+) CGO: (?<cgo>[0-9]+) Ply: (?<players>[0-9]+) Zom: (?<zombies>[0-9]+) Ent: (?<enteties>[0-9() ]+) Items: (?<items>[0-9]+) CO: (?<co>[0-9]+) RSS: (?<rss>[0-9.tgmb]+)", re.IGNORECASE)

#Time: 1324.65m FPS: 37.32 Heap: 2760.7MB Max: 2884.7MB Chunks: 1259 CGO: 71 Ply: 4 Zom: 1 Ent: 17 (206) Items: 7 CO: 4 RSS: 4558.6MB

#entry_types = {
#}

parsers = [
    re_chat,
    re_gmsg,
    re_status,
    re_entity,
]

class LogEntry(object):
    def __init__(self, event):
        self._event = re_event.match(event)
        if not self._event:
            raise ValueError

    @property
    def date(self):
        return self._event.group('date')

    @property
    def time(self):
        return self._event.group('time')

    @property
    def timestamp(self):
        try:
            return datetime.strptime("{0} {1}".format(self.date, self.time), "%Y-%m-%d %H:%M:%S").timestamp()
        except ValueError:
            return None

    def parse(self):
        for parser in parsers:
            m = parser.match(self.message)
            if m:
                print(m.groupdict())

    @property
    def uptime(self):
        return self._event.group('uptime')

    @property
    def loglevel(self):
        return self._event.group('loglevel')

    @property
    def message(self):
        return self._event.group('message')
