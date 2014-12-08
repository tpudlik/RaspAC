import datetime
from flask import Flask, request, session, g, redirect, url_for, \
                  abort, render_template, flash
from contextlib import closing
from google.appengine.ext import ndb

from config import *
                  
app = Flask(__name__)
# Should the next line be removed from the mockup?
app.config.from_object(__name__)


# DB model
class Command(ndb.Model):
    username = ndb.StringProperty()
    command = ndb.StringProperty()
    ts = ndb.DateTimeProperty(auto_now_add=True)


@app.route('/', methods=['GET', 'POST'])
def welcome_page():
    if 'username' in session and session['username']:
        return redirect(url_for('submit_page'))
    error = None
    if request.method == 'POST': # someone's logging in
        if not request.form['username'] in USERNAMES:
            error = 'username'
        elif request.form['password'] != PASSWORD:
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
            submitted_command = Command(username=session['username'],
                                        command=validation_codes['command'])
            submitted_command.put()
            flash("Command submitted (or would have been, it this weren't a mockup!)")
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
    if user_mode not in ACMODES:
        codes['mode_error'] = True
    else:
        codes['mode_error'] = False
    if user_mode is not 'off' and user_temperature not in ACTEMPERATURES:
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
    commands = Command.query().order(-Command.ts)
    command_history = []
    for command in commands:
        if command.command[0] == 'h':
            cmd = 'heat to ' + command.command[4:]
        elif command.command == 'off':
            cmd = 'off'
        else:
            cmd = 'cool to ' + command.command
        command_history.append(dict(command=cmd,
                                    ts=command.ts,
                                    user=command.username))
    return command_history

def last_record():
    """Returns the last temperature and humidity record data.
    
    The returned object is a dict with keys ts, fahrenheit, celsius and
    humidity.
    
    In the mockup, there is no real temperature sensor to query, so 
    an arbitrary result is returned.
    """
    out_record = dict()
    out_record['date'] = "2014-12-08"
    out_record['time'] = "21:38"
    out_record['celsius'] = -4
    out_record['fahrenheit'] = int(round(out_record['celsius']*9/5.0 + 32))
    out_record['humidity'] = 50
    return out_record

# if __name__ == '__main__':
#     app.run(host='0.0.0.0')
