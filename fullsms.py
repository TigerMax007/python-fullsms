#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import options


def send(user, password, gateway, receiver, sender, message):
    pass

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
