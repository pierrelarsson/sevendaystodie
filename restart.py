#!/usr/bin/python3

import sevendaystodie
import logging
import re
import time
import requests
import json

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

t = sevendaystodie.Telnet()
t.connect()
t.loglevel(level='INF', enabled=True)

_re_log = re.compile(r"^(?P<date>[0-9-]*)T(?P<time>[0-9:]*)\s*(?P<uptime>[0-9.]*)\s*(?P<loglevel>[A-Z]*)\s*(?P<message>.*)")

stime = 0
splayers = 0

for n in t:
    m = _re_log.match(n.decode('utf8'))
    if m and m.group('loglevel') == 'INF':
        stat = dict(re.findall(r'(\w+):\s*(\S+)', m.group('message')))
        if 'Time' in stat:
            print(stat)
            stime = int(stat['Time'].split('.', 1)[0])
            splayers = int(stat['Ply'])
            if splayers > 32 and stime > 120:
                break
            if stime > 240:
                break

t.disconnect()
t = sevendaystodie.Telnet()
t.connect()
for n in ['five', 'four', 'three', 'two', 'one']:
    t.say("[FF0000] Restarting in {0} minute(s)".format(n))
    t.command("saveworld")
    time.sleep(60)
t.command("kickall")
time.sleep(5)
t.command("saveworld")
t.command("shutdown")
