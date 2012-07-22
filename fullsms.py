#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import options



if __name__ == '__main__':

    optspec = """
    sms [send | check] [opts] <message>
    --
    u,user= the fullsms.de username
    p,password the fullsms.de password
    r,receiver= the person to send the message to
    g,gateway= the gateway to use
    s,sender= the sender to use
    """
    o = options.Options(optspec)
    (opt, flags, extra) = o.parse(sys.argv[1:])
