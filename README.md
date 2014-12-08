# RaspAC #


An internet-enabled air conditioner remote running on the Raspberry Pi.


## How does it work?  ##

On the software side, an Apache web server running on the Pi serves a
[Flask](http://flask.pocoo.org/) app.  This app makes calls to
[LIRC](http://www.lirc.org/), the Linux Infrared Remote Control library, to
replay previously recorded IR codes.  The Pi is connected to a couple high-
brightness IR diodes which transmit the codes to the air conditioner.

You can play with a mockup of the app [here](http://raspac-mockup.appspot.com).
It will accept the username `Guest` and password `Guest`.


## How to put it together? ##

### Hardware ###

I used the setup [described by Alex Bain](http://alexba.in/blog/2013/03/09/raspberrypi-ir-schematic-for-lirc/),
but I added a [temperature and humidity sensor](http://www.adafruit.com/products/385)
with the data pin connected to pin 4.  See [this tutorial](https://learn.adafruit.com/dht-humidity-sensing-on-raspberry-pi-with-gdocs-logging)
for a circuit schematic.


### Software ###

The software part of this project consists of three pieces: the website that 
lets you communicate with the Raspberry Pi, the temperature sensor code, and
the LIRC, which controls the IR diodes connected to the Pi.  The installation
instructions below assume you're starting from a clean Raspbian installation.


#### Installing and configuring LIRC ####

Follow the instructions
[here](http://alexba.in/blog/2013/01/06/setting-up-lirc-on-the-raspberrypi)
for installing and configuring LIRC.  Note, though, that you will probably be
unable to record the IR codes for your AC using the `irrecord` command line
tool provided with LIRC.  The structure of IR codes used by ACs is different
from that used by TVs, for which `irrecord` was designed to work with.
Rather than telling the AC what button was pressed (e.g., "Increase target
temperature by 2 degrees", or "Switch unit on"), the code contains a complete
description of the new state (e.g., "The fan strength is 3, the temperature
target is 76, the operating mode is cooling, ...").  This structure is not
compatible with `irrecord`.

Fortunately, LIRC provides another command line tool, `mode2`, which will
directly record any sequence of IR pulses and spaces.  You can use it to save
the pulse trains produced by pressing buttons on the remote, and manually
stitch together a LIRC configuration file, `lirc.conf`.  Note that it's in
general not enough to record the effect of pressing each button, since the
signal encodes the full state of the AC.  You will probably want to record
the code associated with each temperature, or even every temperature/mode
combination if your AC supports both heating and cooling modes.  The
`lirc.conf` file I created for my LG AC is provided as an example.

For more information on recording IR codes for ACs using LIRC, see
[here](http://absurdlycertain.blogspot.com/2013/03/lirc-raspi-remote-control-configuration.html).


#### Setting up the temperature sensor ####

I used [C code for the DHT provided by Adafruit](https://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code/tree/master/Adafruit_DHT_Driver).
After compiling `Adafruit_DHT.c` using the Makefile, change its ownership so
that it can be ran without `sudo`:
	
	sudo chown root:root Adafruit_DHT
	sudo chmod +s Adafruit_DHT

Copy the compiled executable to the folder containing `tsensor.py`. Edit the
parameters in `tconfig.py`, then run `tsensor.py` in the background. 
The temperature and humidity sensor will be periodically queried, and the 
results will be recorded in a database.

You will probably want to restart `tsensor.py` every time the Pi is turned on.
I found it most convenient to have a cron job spin it up on every reboot.


#### Setting up the web app ####

Step by step instructions are forthcoming!

For general information on deploying Flask apps on an Apache webserver, see the
[tutorial](http://flask.pocoo.org/docs/0.10/deploying/mod_wsgi/).


## Helpful references ##

The idea of using the Raspberry Pi as an internet-enabled IR remote is not
new, though most people use them to control TVs rather than ACs.  I found 
Alex Bain's description of his [Open Source Universal Remote](http://alexba.in/blog/2013/01/06/setting-up-lirc-on-the-raspberrypi/)
particularly helpful.  Recording the IR codes is discussed by
[Peter Li](http://absurdlycertain.blogspot.com/2013/03/lirc-raspi-remote-control-configuration.html)
in his AC control project.


## Licensing ##

The parts of this software that I have written are covered by the MIT license. This
excludes the following files:

 * `leaves.css`
 * `app.yaml`, `appengine_config.py`, `requirements.txt` and `vendor.py`, 
   which I borrowed from the [Google App Engine Flask template](https://github.com/GoogleCloudPlatform/appengine-python-flask-skeleton).
   These are covered by the Apache license.
