#!/usr/bin/python
"""
tquery: fetch temperature and humidity data from the database
"""

import sqlite3, datetime, json, os
from contextlib import closing
from tconfig import DATABASE

def connect_db():
    return sqlite3.connect(DATABASE, detect_types=sqlite3.PARSE_DECLTYPES)

def get_data():
    """Return temperature and humidity data"""
    # In the future, I'd like to be able to fetch only data from the last
    # day, say.
    with closing(connect_db()) as db:
        cur = db.execute('select ts, temperature, humidity from thdata order by id desc')
        return cur.fetchall()

def get_latest_record():
    """Return latest record from temperature and humidity database"""
    with closing(connect_db()) as db:
        cur = db.execute('SELECT ts, temperature, humidity FROM thdata ORDER BY id DESC LIMIT 1')
        return cur.fetchone()
    
def print_data():
    """Print the database entries."""
    data =  get_data()
    for row in data:
        print 'T = {0}, hum = {1}, time = {2}'.format(row[1], row[2], row[0].strftime("%Y-%m-%d %H:%M:%S"))

def plot_temperature(beginning, end):
    """Produce a plot of temperature over time, from datetime beginning
    to datetime end"""
    # To be written!
    return None

def jsonify():
    """Save the database in a JSON format"""
    output_file = os.path.dirname(DATABASE) + '/temp_humidity.json'
    dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime.datetime) or isinstance(obj, datetime.date) else None
    with open(output_file, 'w') as f:
        f.write(json.dumps(get_data(), indent=4, default=dthandler))

