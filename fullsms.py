#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import urllib
import ConfigParser
import options

BASE_URL = "https://www.fullsms.de/gw/"


USER     = 'user'
PASSWORD = 'password'
GATEWAY  = 'gateway'
RECEIVER = 'receiver'
SENDER   = 'sender'
SETTINGS = [USER, PASSWORD, GATEWAY, RECEIVER, SENDER]

GATEWAYS = dict(('_'+str(g), g) for g in [11, 26, 31, 12, 22, 27, 32])
for key, value in GATEWAYS.items():
    globals()[key] = value

DEFAULTS = dict((zip(SETTINGS, [None] *len(SETTINGS))))
DEFAULTS[GATEWAY] = _22

CODES = {
    200 : 'OK',
    301 : "Syntaxerror: user missing",
    302 : "Syntaxerror: password missing",
    303 : "Syntaxerror: receiver missing",
    304 : "Syntaxerror: gateway missing",
    305 : "Syntaxerror: text missing",
    401 : "Unauthorized (username or password wrong)",
    404 : "Error when sening SMS",
    405 : "User not enabled for HTTP",
    406 : "IP not enabled for HTTP",
    407 : "Massbroadcast not available for this gateway",
    408 : "Massbroadcast not available for this gateway",
    500 : "Unknowen server error, please contact <support@fullsms.de.de>",
    501 : "SMS Text empty",
    502 : "SMS Text too long",
    504 : "Wrong SMS type",
    505 : "Sender too long",
    506 : "Cellphone number invalid",
    507 : "Not enough credits",
    508 : "SMS type requires a sender",
    509 : "SMS type does not allow for a sender",
        }

DEBUG = False

SEND = 'send'
CHECK = 'check'
SUBS = [SEND, CHECK]
optspec = """
sms %s [-d] <message...>
--
 general program options
d,debug     activate debugging
h,help      display help and exit
 for all subcommands
u,user=     the fullsms.de username
p,password= the fullsms.de password
 for 'send' only
g,gateway=  the gateway to use
r,receiver= the person to send the message to
s,sender=   the sender to use
""" % ('[' + ' | '.join(SUBS) + ']')
parser = options.Options(optspec)

def warn(message):
    print "Warning: %s" % message

def fatal(message):
    parser.fatal(message)

def debug(message):
    if DEBUG:
        print "Debug: %s" % message

def parse_config(section='settings', config_filename="~/.fullsms"):
    """ Parse a configuration file with app settings.

    Parameters
    ----------
    section : str
        the name of the config section where to look for settings
        (default: 'settings')
    config_filename : str
        the path to and name of the config file
        (default: '~/.fullsms')

    Returns
    -------
    settings : dict
        any settings found in the config file

    Raises
    ------
    IOError:
        if config_filename does not exist
    NoSectionError
        if no section with name 'section' exists

    """
    config_filename = os.path.expanduser(config_filename)
    cp = ConfigParser.RawConfigParser()
    cp.read(config_filename)
    sets = DEFAULTS.copy()
    sets.update(cp.items(section))
    for key in sets.keys():
        if key not in SETTINGS:
            fatal("Setting '%s' from conf file '%s' not recognized!"
                    % (key, config_filename))
    return sets

def assemble_rest_call(function, parameters):
    """ Create a URL suitable for making a REST call to fullsms.de

    Parameters
    ----------
    function : str
        the api function to execute
    parameters : dict
        the parameters to use in the call

    Returns
    -------
    url : str
        an ready made url

    """
    query = urllib.urlencode(sorted(parameters.items()))
    return "%s%s?%s" % (BASE_URL, function, query)

def call(str_):
    file_like = urllib.urlopen(str_)
    return int(file_like.getcode()), file_like.read()

def assemble_send_str(params):
    return assemble_rest_call('', params)

def assemble_check_str(params):
    return assemble_rest_call('konto.php', params)

def send(user=None,
        password=None,
        gateway=None,
        receiver=None,
        sender=None,
        message=None):
    parameters = {
            'user': user,
            'passwort': password,
            'typ': gateway,
            'handynr': receiver,
            'absender': sender,
            'text': message
            }
    rest_str = assemble_rest_call('', parameters)
    return call(rest_str)

def check(user, password):
    params = {'user': user, 'passwort': password}
    str_ = assemble_check_str(params)
    return call(str_)

def set_setting(setting, conf, cli):
    order = [('default',      DEFAULTS),
             ('conf file',    conf),
             ('command line', cli)]
    prev, val = None, None
    for desc, container in order:
        if container[setting] is not None:
            if val is not None:
                val = container[setting]
                debug("Value for '%s' found on %s, overrides %s: '%s'"
                        % (setting, desc, prev, val))
            else:
                val = container[setting]
                debug("Value for '%s' found in %s: '%s'"
                        % (setting, desc, val))
        prev = desc
    if val is None:
        warn("No value for '%s' found " % setting)
    return val

if __name__ == '__main__':
    (opt, flags, extra) = parser.parse(sys.argv[1:])
    if opt.debug:
        DEBUG = True
        debug('Activate debug')
    if len(extra) == 0:
        parser.fatal('No subcommand given')
    sub = extra[0]
    if sub not in SUBS:
        fatal("invalid subcommand: %s" % sub)
    cfs, params = parse_config(), {}
    for s in SETTINGS:
        r = set_setting(s, cfs, opt)
        locals()[s] = params[s] = r
    if user is None or password is None:
        fatal('No username or password')

    if sub == CHECK:
        code, result = check(user, password)
        if code == 200:
            print "The current balance for the account '%s' is: %s €" \
            % (user, result)
        else:
            fatal("Error checking balance")
    elif sub == SEND:
        mess = ' '.join(extra[1:])
        if len(mess) == 0:
            fatal('No message to send')
        params['message'] = mess
        if receiver is None:
            fatal('No receiver')
        code, result = send(**params)
        # HTTP return code seems always to be 200
        # check result instead
        result = int(result)
        if result == 200:
            debug('Send successful!')
        else:
            fatal('Error code: %d - %s' % (result, CODES[result]))
