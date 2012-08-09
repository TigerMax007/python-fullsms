Description
===========

A library and command line interface to the HTTP interface of `fullsms.de
<http://fullsms.de>`_, which makes use of Avery Pennarun's excellent
``options.py``.

Note: If you do not already have an account on ``fullsms.de``, please consider
using the following link `https://www.fullsms.de/?ref=101584
<https://www.fullsms.de/?ref=101584>`_ to register. This will credit the
account of the author of ``fullsms.py`` with ``15,00 €``.

Example command line usage
==========================

Under the assumption that a correct ``user`` and ``password`` are stored in the
config file (see below), the two subcommands ``send`` to send a message and
``check`` to the check the balance for an account can be used as follows:

Send a text message, specifying the recipient with the ``[-r | --receiver]``
switch::

    $ sms send -r 0123456789 "Hello honey, I'm home"

Check account balance::

    $ sms check
    The current balance for the account 'MaxMusterman' is: 12.571 €

For all available options, use::

    $ sms -h

Note: if you are using the script from a cron-job you can silence the output
using ``[-q | --quiet]`` switch.

Example library usage
=====================

The ``python-fullsms`` can easily be used as a python module::

    >>> import fullsms

    >>> fullsms.send(user=MaxMusterman,
                     password=maxmustermangeheim,
                     gateway=21,
                     receiver=0123456789,
                     sender=0123456789,
                     message="Hello honey, I'm home")
    (200 : 'OK')

    >>> fullsms.check(user=MaxMusterman, password=maxmustermangeheim)
    (200, '12.571'

Example Config
==============

Default settings can be stored in the file ``~/.fullsms``::

    [settings]
    user     = MaxMusterman
    password = maxmustermangeheim
    gateway  = 11
    sender   = 0123456789
    receiver = 0123456789

Note: If you wish to use an alternative file, use the ``[-c | --config]``
switch.

Phonebook
=========

A rudimentary phonebook file is supported. By default, the script searches
``~/.fullsms-book`` for entries in a section titled ``contacts``::

    [contacts]
    max = 0123456789
    maxine = 1234567890
    maximilian = 2345678901

Thus you can use these defined aliases on the command line::

    $ sms send -r maxine "Hello honey, I'm home"

Using the ``[-e | --expand]`` command-line switch to expand the sender from the
phonebook too, the following will send a message to ``maxine`` looking like it
came from ``maximilian``::

    $ sms send -r maxine -s maximilian "Any plans for tonight?"

Note however, that setting an arbitrary sender may or may not be supported by
the gateway.

Author and Copyright
====================

* ``fullsms.py`` is © 2012 Valentin Haenel, under a 2-Clause BSD license
* ``options.py`` is © 2010-2012 Avery Pennarun, under a 2-Clause BSD license

``options.py`` is included verbatim in the file ``fullsms.py`` to make
installation and usage so much easier. The copied code is clearly marked and
the original copyright statement etc. is included as required by the licence.
