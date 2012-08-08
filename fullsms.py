#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2012 Valentin Haenel
# All rights reserved.
#
# (This license applies to all code in this file except options.py. The
# options.py copy is included verbatim at the beginning of this file, it's
# copyright is included and the copied parts are clearly marked)
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#    1. Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#
#    2. Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in
#       the documentation and/or other materials provided with the
#       distribution.
#
# THIS SOFTWARE IS PROVIDED BY VALENTIN HAENEL ``AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import sys
import os
import urllib
import ConfigParser

###############################################################################
# options.py which was copied verbatim from bup starts here                   #
###############################################################################

# Copyright 2010-2012 Avery Pennarun and options.py contributors.
# All rights reserved.
#
# (This license applies to this file but not necessarily the other files in
# this package.)
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#    1. Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#
#    2. Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in
#       the documentation and/or other materials provided with the
#       distribution.
#
# THIS SOFTWARE IS PROVIDED BY AVERY PENNARUN ``AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
"""Command-line options parser.
With the help of an options spec string, easily parse command-line options.

An options spec is made up of two parts, separated by a line with two dashes.
The first part is the synopsis of the command and the second one specifies
options, one per line.

Each non-empty line in the synopsis gives a set of options that can be used
together.

Option flags must be at the begining of the line and multiple flags are
separated by commas. Usually, options have a short, one character flag, and a
longer one, but the short one can be omitted.

Long option flags are used as the option's key for the OptDict produced when
parsing options.

When the flag definition is ended with an equal sign, the option takes one
string as an argument. Otherwise, the option does not take an argument and
corresponds to a boolean flag that is true when the option is given on the
command line.

The option's description is found at the right of its flags definition, after
one or more spaces. The description ends at the end of the line. If the
description contains text enclosed in square brackets, the enclosed text will
be used as the option's default value.

Options can be put in different groups. Options in the same group must be on
consecutive lines. Groups are formed by inserting a line that begins with a
space. The text on that line will be output after an empty line.
"""
import sys, os, textwrap, getopt, re, struct


def _invert(v, invert):
    if invert:
        return not v
    return v


def _remove_negative_kv(k, v):
    if k.startswith('no-') or k.startswith('no_'):
        return k[3:], not v
    return k,v


class OptDict(object):
    """Dictionary that exposes keys as attributes.

    Keys can be set or accessed with a "no-" or "no_" prefix to negate the
    value.
    """
    def __init__(self, aliases):
        self._opts = {}
        self._aliases = aliases

    def _unalias(self, k):
        k, reinvert = _remove_negative_kv(k, False)
        k, invert = self._aliases[k]
        return k, invert ^ reinvert

    def __setitem__(self, k, v):
        k, invert = self._unalias(k)
        self._opts[k] = _invert(v, invert)

    def __getitem__(self, k):
        k, invert = self._unalias(k)
        return _invert(self._opts[k], invert)

    def __getattr__(self, k):
        return self[k]


def _default_onabort(msg):
    sys.exit(97)


def _intify(v):
    try:
        vv = int(v or '')
        if str(vv) == v:
            return vv
    except ValueError:
        pass
    return v


def _atoi(v):
    try:
        return int(v or 0)
    except ValueError:
        return 0


def _tty_width():
    s = struct.pack("HHHH", 0, 0, 0, 0)
    try:
        import fcntl, termios
        s = fcntl.ioctl(sys.stderr.fileno(), termios.TIOCGWINSZ, s)
    except (IOError, ImportError):
        return _atoi(os.environ.get('WIDTH')) or 70
    (ysize,xsize,ypix,xpix) = struct.unpack('HHHH', s)
    return xsize or 70


class Options:
    """Option parser.
    When constructed, a string called an option spec must be given. It
    specifies the synopsis and option flags and their description.  For more
    information about option specs, see the docstring at the top of this file.

    Two optional arguments specify an alternative parsing function and an
    alternative behaviour on abort (after having output the usage string).

    By default, the parser function is getopt.gnu_getopt, and the abort
    behaviour is to exit the program.
    """
    def __init__(self, optspec, optfunc=getopt.gnu_getopt,
                 onabort=_default_onabort):
        self.optspec = optspec
        self._onabort = onabort
        self.optfunc = optfunc
        self._aliases = {}
        self._shortopts = 'h?'
        self._longopts = ['help', 'usage']
        self._hasparms = {}
        self._defaults = {}
        self._usagestr = self._gen_usage()  # this also parses the optspec

    def _gen_usage(self):
        out = []
        lines = self.optspec.strip().split('\n')
        lines.reverse()
        first_syn = True
        while lines:
            l = lines.pop()
            if l == '--': break
            out.append('%s: %s\n' % (first_syn and 'usage' or '   or', l))
            first_syn = False
        out.append('\n')
        last_was_option = False
        while lines:
            l = lines.pop()
            if l.startswith(' '):
                out.append('%s%s\n' % (last_was_option and '\n' or '',
                                       l.lstrip()))
                last_was_option = False
            elif l:
                (flags,extra) = (l + ' ').split(' ', 1)
                extra = extra.strip()
                if flags.endswith('='):
                    flags = flags[:-1]
                    has_parm = 1
                else:
                    has_parm = 0
                g = re.search(r'\[([^\]]*)\]$', extra)
                if g:
                    defval = _intify(g.group(1))
                else:
                    defval = None
                flagl = flags.split(',')
                flagl_nice = []
                flag_main, invert_main = _remove_negative_kv(flagl[0], False)
                self._defaults[flag_main] = _invert(defval, invert_main)
                for _f in flagl:
                    f,invert = _remove_negative_kv(_f, 0)
                    self._aliases[f] = (flag_main, invert_main ^ invert)
                    self._hasparms[f] = has_parm
                    if f == '#':
                        self._shortopts += '0123456789'
                        flagl_nice.append('-#')
                    elif len(f) == 1:
                        self._shortopts += f + (has_parm and ':' or '')
                        flagl_nice.append('-' + f)
                    else:
                        f_nice = re.sub(r'\W', '_', f)
                        self._aliases[f_nice] = (flag_main,
                                                 invert_main ^ invert)
                        self._longopts.append(f + (has_parm and '=' or ''))
                        self._longopts.append('no-' + f)
                        flagl_nice.append('--' + _f)
                flags_nice = ', '.join(flagl_nice)
                if has_parm:
                    flags_nice += ' ...'
                prefix = '    %-20s  ' % flags_nice
                argtext = '\n'.join(textwrap.wrap(extra, width=_tty_width(),
                                                initial_indent=prefix,
                                                subsequent_indent=' '*28))
                out.append(argtext + '\n')
                last_was_option = True
            else:
                out.append('\n')
                last_was_option = False
        return ''.join(out).rstrip() + '\n'

    def usage(self, msg=""):
        """Print usage string to stderr and abort."""
        sys.stderr.write(self._usagestr)
        if msg:
            sys.stderr.write(msg)
        e = self._onabort and self._onabort(msg) or None
        if e:
            raise e

    def fatal(self, msg):
        """Print an error message to stderr and abort with usage string."""
        msg = '\nerror: %s\n' % msg
        return self.usage(msg)

    def parse(self, args):
        """Parse a list of arguments and return (options, flags, extra).

        In the returned tuple, "options" is an OptDict with known options,
        "flags" is a list of option flags that were used on the command-line,
        and "extra" is a list of positional arguments.
        """
        try:
            (flags,extra) = self.optfunc(args, self._shortopts, self._longopts)
        except getopt.GetoptError, e:
            self.fatal(e)

        opt = OptDict(aliases=self._aliases)

        for k,v in self._defaults.iteritems():
            opt[k] = v

        for (k,v) in flags:
            k = k.lstrip('-')
            if k in ('h', '?', 'help', 'usage'):
                self.usage()
            if (self._aliases.get('#') and
                  k in ('0','1','2','3','4','5','6','7','8','9')):
                v = int(k)  # guaranteed to be exactly one digit
                k, invert = self._aliases['#']
                opt['#'] = v
            else:
                k, invert = opt._unalias(k)
                if not self._hasparms[k]:
                    assert(v == '')
                    v = (opt._opts.get(k) or 0) + 1
                else:
                    v = _intify(v)
            opt[k] = _invert(v, invert)
        return (opt,flags,extra)

###############################################################################
# options.py which was copied verbatim from bup ends here                     #
###############################################################################

BASE_URL = "https://www.fullsms.de/gw/"

USER      = 'user'
PASSWORD  = 'password'
GATEWAY   = 'gateway'
RECEIVER  = 'receiver'
SENDER    = 'sender'
PHONEBOOK = 'phonebook'
# settings only relevant for the fullsms http interface
API_SETTINGS = [USER, PASSWORD, GATEWAY, RECEIVER, SENDER]
# all settings
SETTINGS = API_SETTINGS + [PHONEBOOK]

class Gateway(object):
    """ Simple object to store gateway attributes.

    Parameters
    ----------
    id_ : int
        the integer identifier
    limit : int
        the maximum allowed message length for this gateway
    own: bool
        if the gateway allows setting 'sender'
    """
    def __init__(self, id_, limit, own):
        self.id_, self.limit, self.own = id_, limit, own
    def __str__(self):
        return str(self.id_)

GATEWAYS = dict((str(g[0]), Gateway(*g)) for g in
        [(11, 1560, True ),
         (26,  800, False),
         (31,  160, False),
         (12, 1560, True ),
         (22,  800, True ),
         (27,  800, False),
         (32,  160, False),
        ])

DEFAULTS = dict((zip(SETTINGS, [None] * len(SETTINGS))))
DEFAULTS[GATEWAY] = GATEWAYS[str(22)]
DEFAULT_CONFIG_FILE = "~/.fullsms"
DEFAULT_PHONE_BOOK = "~/.fullsms-book"
DEFAULTS[PHONEBOOK] = DEFAULT_PHONE_BOOK

QUIET = False
DEBUG = False
DRY_RUN = False
DRY_RUN_CODE = 666

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
    # special option for python-fullsms only
    DRY_RUN_CODE : "No REST call made, probably using '--dry-run'"
        }

SEND = 'send'
CHECK = 'check'
SUBS = [SEND, CHECK]
def default(str_):
    return "(default '%s')" % str_
optspec = """
sms %s [OPTIONS] <message...>
--
 general program options
q,quiet       silence all outpt
d,debug       activate debugging
h,help        display help and exit
c,config=     the config file to use %s
y,dry-run     don't perform any REST calls
 for all subcommands
u,user=       the fullsms.de username
p,password=   the fullsms.de password
 for 'send' only
g,gateway=    the gateway to use %s
r,receiver=   the person to send the message to
s,sender=     the sender to use
 phonebook management
b,phonebook=  the phonebook file
""" % tuple(['[' + ' | '.join(SUBS) + ']'] +
        map(default, (DEFAULT_CONFIG_FILE, DEFAULTS[GATEWAY])))
parser = Options(optspec)

def info(message):
    """ Informational messages. """
    if not QUIET:
        print "Info:    %s" % message

def warn(message):
    """ Warnings. """
    if not QUIET:
        print "Warning: %s" % message

def debug(message):
    """ Debug messages """
    if DEBUG and not QUIET:
        print "Debug:   %s" % message

def fatal(message):
    """ Errors related to parsing. """
    parser.fatal(message)

def error(message):
    """ General program errors. """
    print "Error:       %s" % message
    sys.exit(2)

class UnknownSettingError(Exception):
    """ Raised when an unknown setting is encounterd in a config file. """
    pass

def open_config(config_filename):
    """ Open a config-file.

    Parameters
    ----------
    config_filename : str
        the path to and name of the config file

    Raises
    ------
    IOError:
        if config_filename does not exist

    """
    config_filename = os.path.expanduser(config_filename)
    return open(config_filename)

def parse_config(config_fp, section='settings'):
    """ Parse a configuration file with app settings.

    Parameters
    ----------
    config_fp : file-like
        the file-pointer to the config file
    section : str
        the name of the config section where to look for settings
        (default: 'settings')

    Returns
    -------
    settings : dict
        any settings found in the config file

    Raises
    ------
    NoSectionError
        if no section with name 'section' exists
    UnknownSettingError
        if an unknown setting is present in the configuration

    """
    cp = ConfigParser.RawConfigParser()
    cp.readfp(config_fp)
    sets = dict(cp.items(section))
    for key in sets.keys():
        if key not in SETTINGS:
            raise UnknownSettingError(
                "Setting '%s' from conf file '%s' not recognized!"
                    % (key, config_fp.name))
    return sets

def parse_phonebook(phonebook_fp, section='contacts'):
    """ Parse the phonebook.

    Parameters
    ----------
    phonebook_fp : file-like
        the file-pointer to the phonebook file
    section : str
        the section of the entries, default: 'contacts'

    Returns
    -------
    contacts : dict str -> str
        the contacts name -> number

    Raises
    ------
    NoSectionError
        if no section with the name 'section' is present
    """
    cp = ConfigParser.RawConfigParser()
    cp.readfp(phonebook_fp)
    contacts = dict(cp.items(section))
    if DEBUG:
        max_len = max(map(len, contacts.keys())) + 4
        debug("Phonebook at '%s' has the following entries:"
                % phonebook_fp.name)
        for name, number  in contacts.items():
            debug('%s : %s' % (name.ljust(max_len), number))
    return contacts

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
    call_string = "%s%s?%s" % (BASE_URL, function, query)
    debug("REST call string: '%s'" % call_string)
    return call_string

def call(str_):
    """ Perform rest call and return (code, message). """
    if not DRY_RUN:
        file_like = urllib.urlopen(str_)
        return int(file_like.getcode()), file_like.read()
    else:
        return DRY_RUN_CODE, DRY_RUN_CODE

def assemble_send_str(params):
    """ Turn params dict into URL for send. """
    return assemble_rest_call('', params)

def assemble_check_str(params):
    """ Turn params dict into URL for check. """
    return assemble_rest_call('konto.php', params)

def send(user=None,
        password=None,
        gateway=None,
        receiver=None,
        sender=None,
        message=None):
    """ Implements send command. """
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
    """ Implements check command. """
    params = {'user': user, 'passwort': password}
    str_ = assemble_check_str(params)
    return call(str_)

def set_setting(setting, conf, cli):
    """ Extract the value for setting in order.

    Parameters
    ----------
    setting : str
        the setting to look for
    conf : dict
        the dictionary from the configuration file
    cli : dict like
        the magic dictionary from the command line

    Returns
    -------
    val : str
        an appropriate value for setting

    """
    order = [('defaults',      DEFAULTS),
             ('conf file',    conf),
             ('command line args', cli)]
    prev, val, prev_val = None, None, None
    for desc, container in order:
        if container[setting] is not None:
            prev_val, val = val, container[setting]
            if prev_val is not None:
                debug("Value for '%s' found in '%s', overrides setting from '%s': '%s'"
                        % (setting, desc, prev, val))
            else:
                debug("Value for '%s' found in '%s': '%s'"
                        % (setting, desc, val))
        prev = desc
    if val is None:
        debug("No value for '%s' found anywhere" % setting)
    return val

def check_gateway(str_):
    """ Ensure that the gateway is valid. """
    try:
        return GATEWAYS[str(str_)]
    except KeyError:
        raise ValueError("Gateway: '%s' is not defined." % str_)

def check_sender(str_):
    """ Check sender format. """
    if not (re.search(r"^[0-9]{0,15}$", str(str_)) or
            re.search(r"^\w{0,15}$", str(str_))):
        raise ValueError(
            "Sender should be 11 alphanumeric or 15 numeric characters, " +\
                    "but was: '%s'" % str_)

if __name__ == '__main__':
    (opt, flags, extra) = parser.parse(sys.argv[1:])
    if not sum([x is not None for x in (opt.debug, opt.quiet)]) <= 1:
        fatal("'debug' and 'quiet' are mutually exclusive.")
    if opt.debug:
        DEBUG = True
        debug('Activate debug')
    elif opt.quiet:
        QUIET = True
    if opt.dry_run:
        DRY_RUN = True
    if len(extra) == 0:
        fatal('No subcommand given')
    sub = extra[0]
    if sub not in SUBS:
        fatal("invalid subcommand: %s" % sub)

    # empty config_file pointer
    config_fp = None
    config_filename = opt.config if opt.config is not None \
            else DEFAULT_CONFIG_FILE
    # settings dict with all None and empty params dict
    config_file_settings, params = \
            dict((zip(SETTINGS, [None] * len(SETTINGS)))), {}
    # try opening the config file
    try:
        config_fp = open_config(config_filename)
        debug("Config file at '%s'" % config_fp.name)
    except IOError:
        debug("No config file at '%s'" % config_filename)
    else:
        try:
            # read the settings from the file
            config_file_settings_temp = parse_config(config_fp)
            # and update the config file settings
            config_file_settings.update(config_file_settings_temp)
        except UnknownSettingError as use:
            error(use)
    finally:
        if config_fp is not None:
            config_fp.close()
    # select the setting with the highest precedence
    for s in SETTINGS:
        locals()[s] = set_setting(s, config_file_settings, opt)
        if s in API_SETTINGS:
            params[s] = locals()[s]

    if user is None or password is None:
        fatal('No username and/or password')
    elif sub == CHECK:
        debug("Ignoring: '%s' for '%s'" %
                ([s for s in (SENDER, RECEIVER, GATEWAY, PHONEBOOK)
                    if locals()[s] is not None],
                    CHECK))
        code, result = check(user, password)
        # under the assumption, that result contains a '.' if its a valid
        # balance
        if '.' in result:
            info("The current balance for the account '%s' is: %s €" \
            % (user, result))
        else:
            result = int(result)
            error("Failed checking, error code: %d - %s"
                    % (result, CODES[result]))
    elif sub == SEND:
        # check the gateway argument
        try:
            gateway = check_gateway(params[GATEWAY])
        except ValueError as ve:
            fatal(ve)

        # prepare the message and check its validity
        mess = ' '.join(extra[1:])
        mess_len = len(mess)
        debug("Message: '%s', length: '%d'" % (mess, mess_len))
        if mess_len == 0:
            fatal('No message to send')
        elif mess_len > gateway.limit:
            fatal("Message too long: '%d', gateway has max length: '%d'"
                    % (mess_len, gateway.limit))
        params['message'] = mess

        # check the sender argument
        try:
            check_sender(sender)
        except ValueError as ve:
            fatal(ve)

        # make sure we have some kind of receiver
        if receiver is None:
            fatal('No receiver')

        # try to open the phonebook and expand the receiver
        try:
            with open_config(phonebook) as phonebook_fp:
                contacts = parse_phonebook(phonebook_fp)
        except IOError:
            debug("No phonebook at: '%s'" % phonebook)
        else:
            # try to expand receiver from the phone book
            if receiver in contacts:
                debug("Expanding '%s' to '%s' via phonebook"
                        % (receiver, contacts[receiver]))
                receiver = contacts[receiver]
            else:
                debug("Value '%s' not found in phonebook" % receiver)

        # perform the sending
        code, result = send(**params)

        # HTTP return code seems always to be 200
        # check result instead
        result = int(result)
        if result == 200:
            info('Send successful!')
        else:
            error('Failed sending, error code: %d - %s'
                    % (result, CODES[result]))
