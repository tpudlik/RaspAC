import sqlite3
import subprocess, datetime
from flask import Flask, request, session, g, redirect, url_for, \
                  abort, render_template, flash
from contextlib import closing
from tquery import get_latest_record
from config import *
                  
app = Flask(__name__)
app.config.from_object(__name__)

# DB helper functions
def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    """Initializes the sqlite3 database.  This function must be imported and
    executed from the Python interpreter before the application is first run."""
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

# Auto-open and close DB when serving requests
@app.before_request
def before_request():
    g.db = connect_db()
    
@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()
        
@app.route('/', methods=['GET', 'POST'])
def welcome_page():
    if 'username' in session and session['username']:
        return redirect(url_for('submit_page'))
    error = None
    if request.method == 'POST': # someone's logging in
        if not request.form['username'] in app.config['USERNAMES']:
            error = 'username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'password'
        else: # successful login
            session['username'] = request.form['username']
            flash('Hi ' + session['username'] + '!')
            return redirect(url_for('submit_page'))
    return render_template('welcome_page.html', commands=command_history(),
                           error=error, last_record=last_record())

@app.route('/submit', methods=['GET', 'POST'])
def submit_page():
    error = None
    if not session.get('username'):
        abort(401)
    if request.method == 'POST': # command is being issued to AC
        user_mode = request.form['mode']
        user_temperature = request.form['temperature']
        validation_codes = validate_AC_command(user_mode, user_temperature)
        if (validation_codes['mode_error'] or
            validation_codes['temperature_error']):
            error=validation_codes
        else:
            subprocess.call(['/usr/bin/irsend','SEND_ONCE', 'lgac',
                             validation_codes['command']])
            g.db.execute('insert into commands (command, ts, user) values (?, ?, ?)',
                         [validation_codes['command'],
                          datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                          session['username']])
            g.db.commit()
            flash('Command submitted')
    return render_template('submit_page.html', commands=command_history(),
                           error=error, last_record=last_record())

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('welcome_page'))
    
def validate_AC_command(user_mode, user_temperature):
    """Validates and sanitizes user-input command; translates command
    into irsend call."""
    codes = dict()
    if user_mode not in app.config['ACMODES']:
        codes['mode_error'] = True
    else:
        codes['mode_error'] = False
    if user_mode is not 'off' and user_temperature not in app.config['ACTEMPERATURES']:
        codes['temperature_error'] = True
    else:
        codes['temperature_error'] = False
    if not codes['mode_error'] and not codes['temperature_error']:
        codes['mode'] = user_mode
        codes['temperature'] = user_temperature
        if codes['mode'] == 'off':
            command_postfix = 'off'
        elif codes['mode'] == 'heat':
            command_postfix = 'heat' + codes['temperature']
        else:
            command_postfix = codes['temperature']
        codes['command'] = command_postfix
    return codes
            
def command_history():
    """Returns a list of  dictionaries, each containing a command issued
    to the AC previously.  The list is ordered chronologically, from newest
    to oldest."""
    cur = g.db.execute('select command, ts, user from commands order by id desc')
    command_history = []
    for row in cur.fetchall():
        if row[0][0] == 'h':
            cmd = 'heat to ' + row[0][4:]
        elif row[0] == 'off':
            cmd = 'off'
        else:
            cmd = 'cool to ' + row[0]
        command_history.append(dict(command=cmd, ts=row[1], user=row[2]))
    return command_history

def last_record():
    """Returns the last temperature and humidity record data.
    
    The returned object is a dict with keys ts, fahrenheit, celsius and
    humidity.
    """
    db_record = get_latest_record()
    out_record = dict()
    out_record['date'] = db_record[0].strftime("%Y-%m-%d")
    out_record['time'] = db_record[0].strftime("%H:%M")
    out_record['celsius'] = db_record[1]
    out_record['fahrenheit'] = int(round(out_record['celsius']*9/5.0 + 32))
    out_record['humidity'] = int(round(db_record[2]))
    return out_record

if __name__ == '__main__':
    app.run(host='0.0.0.0')
