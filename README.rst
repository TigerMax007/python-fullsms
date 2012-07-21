Description
===========

A library and command line interface to the HTTP interface of ``fullsms.de``.

Example command line usage
==========================

Send a text message::

    $ fullsms send -r 012345678 -m "Hello honey, I'm home"

Check account balance::

    $ fullsms check

Example library usage
=====================

The ``python-fullsms`` can easily be used as a python module::

    >>> import fullsms

    >>> fullsms.send(gateway=12, receiver=0123456789)
    500 : 'OK'

    >>> fullsms.check()
    Current Balance: 23,42 €

Example Config
==============

Default settings can be stored in the file ``.fullsms``::

    [settings]
        username = "Max Musterman"
        passwort = maxmustermangeheim
        default_gateway = 11
        default_sender  = 0123456789

