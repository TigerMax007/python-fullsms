Description
===========

A library and command line interface to the HTTP interface of `fullsms.de
<http://fullsms.de>`_.

Note: this script makes use of Avery Pennarun's excellent
``options.py`` (`blog post<http://apenwarr.ca/log/?m=201111#02>`_).

Note: If you do not already have an account on ``fullsms.de``, please consider
using the following link `https://www.fullsms.de/?ref=101584
<https://www.fullsms.de/?ref=101584>`_ to register. This will credit the
account of the author of ``fullsms.py`` with ``15,00 €``.


Synposis
--------

There are two subcommands ``check`` and ``send``::

    $ sms [GENERAL-OPTIONS] < check | send > [SPECIFIC-OPTIONS]

The specific invocations are::

    $ sms -h
    $ sms -v
    $ sms [ -q | -d ] [ -y ] [ -c <config> ] check
          [ -u <user> ] [ -p <password> ]
    $ sms [ -q | -d ] [ -y ] [ -c <config> ] send
          [ -u <user> ] [ -p <password> ]
          [ -g <gateway> ] [ -r <receiver> ] [ -s <sender> ]
          [ -p <phonebook> ] [ -e ] [ -i ]
          <message>

Because of the way ``options.py`` works, the general program options and
subcommand options can be mixed and can be placed before or after the
subcommand itself. Also, options which are relevant only for ``send`` can be
given when using ``check`` and will be silently ignored.

Command Line Options
--------------------

* Descriptive options

``-h, --help`` :
    Display help and exit.
``-v, --version`` :
    Display version number and exit.

* General program options

``-q, --quiet`` :
    Silence all output. Useful when executing the script from a cronjob.
``-d, --debug`` :
    Activate debugging. Will output noisly what is being done.
``-y, --dry-run`` :
    Don't perform any REST calls. Useful in combination with ``-y, --dry-run``.
``-c, --config <config>`` :
    The config file to use (default ``~/.fullsms``). Useful if you have
    multiple configurations.

* For all subcommands

``-u, --user <user>`` :
    The ``fullsms.de`` username.
``-p, --password <password>`` :
    The ``fullsms.de`` password.

* For ``send`` only

``-g, --gateway <gateway>`` :
    The gateway to use (default ``22``). ``fullsms.de`` has multiple gateways,
    see below for details.
``-r, --receiver <receiver>`` :
    The person to send the message to.
``-s, --sender <sender>`` :
    The sender to use. Can be 11 alphanumeric or 15 numric characters.

* Phonebook management

``-b, --phonebook <phonebook>`` :
    The phonebook file (default ``~/.fullsms- book``). See below for details
    about this file.
``-e, --expand`` :
    Expand sender from the phonebook. This means, that if the sender name is found
    in the phonebook, the corresponding number will be used as a sender.
``-i, --ignore`` :
    Ignore errors when expanding receiver. The most common use case is to send
    messages to people in your phonebook. To avoid typos, the script will abort
    if the given receiver is not in your phone book. This option disables this
    behaviour. If you wish to disable this b default, consider using the config
    file.

Note: since ``[-e | --expand]`` and ``[-i | --ignore]`` can also be specified
in the config file, you may need a way to revert these if they are set to
``true``. Courtesy of ``options.py`` we have the negation options
``--no-expand`` and ``--no-ignore`` at no additional cost which will do exactly
that.

Config file
-----------

``python-fullsms`` can be configured using a config file, usually located at
``~/.fullsms`` and whose syntax is a common INI file and contains a single
``settings`` section. The most common use case is to save the ``user``,
``password`` and ``sender`` settings. This way, you need to specify only the
receiver and the message on the command line.

The settings given in the config file take precedence over the default values.
Whereas the options given on the command line always take precedence over those
given in the config file. Using the ``[-d | --debug]`` options shows exactly
which settings where obtained from where and which ones took precedence.

The following settings are supported in the config file which correspond
directly to their command line counterparts:

* ``user``
* ``password``
* ``gateway``
* ``receiver``
* ``sender``
* ``phonebook``
* ``expand``
* ``ignore``

The two settings ``expand`` and ``ignore`` are booleans and must take either
the value ``true`` or ``false`` (or any semantically reasonable or case
insensitive equivalent). All others are strings.

Example::

    [settings]
    user      = MaxMusterman
    password  = maxmustermangeheim
    gateway   = 11
    receiver  = 0123456789
    sender    = 0123456789
    phonebook = ~/.mybook
    expand    = False
    ignore    = True

Reminder: If you wish to use an alternative file, use the ``[-c | --config]``
option.

Example command line usage
--------------------------

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
---------------------

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


Phonebook
---------

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

    $ sms send -r maxine -e -s maximilian "Any plans for tonight?"

Note however, that setting an arbitrary sender may or may not be supported by
the gateway.

Author and Copyright
--------------------

* ``fullsms.py`` is © 2012 Valentin Haenel, under a 2-Clause BSD license
* ``options.py`` is © 2010-2012 Avery Pennarun, under a 2-Clause BSD license

``options.py`` is included verbatim in the file ``fullsms.py`` to make
installation and usage so much easier. The copied code is clearly marked and
the original copyright statement etc. is included as required by the licence.
