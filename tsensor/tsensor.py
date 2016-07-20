#!/usr/bin/python
"""
tsensor: reading and recording temperature and humidity from DHT 22
"""

import sqlite3, re, datetime, subprocess, time
from contextlib import closing
from tconfig import DATABASE, BIN, DELAY

def connect_db():
    return sqlite3.connect(DATABASE)

def init_db():
    """Initialize SQLite database for storing data.  Hopefully to be executed
    only once, before the application is first run."""
    with closing(connect_db()) as db:
        with closing(open('schema.sql', mode='r')) as f: # based on flask tutorial
            db.cursor().executescript(f.read())
        db.commit()

def append_db(timestamp, temperature, humidity):
    """Append entry to the database"""
    with closing(connect_db()) as db:
        db.execute('insert into thdata (ts, temperature, humidity) values (?, ?, ?)',
                   [timestamp, temperature, humidity])
        db.commit()

def get_temperature():
    """Poll the sensor for the temperature and humidity values.  If the polling
    fails, wait 3 seconds and try again.  Repeat until successful."""
    output = subprocess.check_output([BIN + "/Adafruit_DHT", "22", "4"]);
    tmatches = re.search("Temp =\s+([0-9.]+)", output)
    hmatches = re.search("Hum =\s+([0-9.]+)", output)
    if not tmatches:
        time.sleep(3)
        return get_temperature()
    temp = float(tmatches.group(1))
    hum = float(hmatches.group(1))
    return (temp, hum)

if __name__ == '__main__':
    while True:
        (temp, hum) = get_temperature()
        timestamp = datetime.datetime.now()
        append_db(timestamp, temp, hum)
        time.sleep(DELAY)
