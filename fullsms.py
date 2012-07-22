#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import urllib
import options

BASE_URL = "https://www.fullsms.de/gw/"

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
    return file_like.read()

def send(user, password, gateway, receiver, sender, message):
    parameters = {
            'user': user,
            'passwort': password,
            'typ': gateway,
            'handynr': receiver,
            'absender': sende,
            'text': message
            }
    rest_str = assemble_rest_call('', parameters)
    return call(rest_str)

def check(user, password):
    parameters = {
            'user': user,
            'passwort': password,
            }
    rest_str = assemble_rest_call('konto.php', parameters)
    return call(rest_str)

if __name__ == '__main__':

    optspec = """
    sms [send | check] [opts] <message>
    --
    u,user= the fullsms.de username
    p,password the fullsms.de password
    g,gateway= the gateway to use
    r,receiver= the person to send the message to
    s,sender= the sender to use
    """
    o = options.Options(optspec)
    (opt, flags, extra) = o.parse(sys.argv[1:])
