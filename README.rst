Description
===========

Send sms from the command line.

A library and command line interface to the HTTP interface of `fullsms.de
<http://fullsms.de>`_.

Note: this script makes use of Avery Pennarun's excellent
``options.py`` (`blog post <http://apenwarr.ca/log/?m=201111#02>`_).

Note: If you do not already have an account on ``fullsms.de``, please consider
using the following link `https://www.fullsms.de/?ref=101584
<https://www.fullsms.de/?ref=101584>`_ to register. This will credit the
account of the author of ``python-fullsms`` with ``15,00 €``.

``fullsms.de`` Documentation
----------------------------

There are two PDFs provided by ``fullsms.de`` which describe both the HTTP
interface and the available gateways.

* `Description of the HTTP interface <https://www.fullsms.de/dokumente/fullsms-SMS-Versand.pdf>`_
* `Description of the available gateways <https://www.fullsms.de/dokumente/fullsms-SMS-Gateway-Beschreibung.pdf>`_

Synposis
--------

There are three subcommands ``pb`` to print the phone-book, ``check`` to check
the account balance and ``send`` to send sms::

    $ sms [GENERAL-OPTIONS] < check | send | pb > [SPECIFIC-OPTIONS]

The specific invocations are::

    $ sms -h
    $ sms -v
    $ sms [ -q | -d ] [ -y ] [ -c <config> ] check
          [ -u <user> ] [ -p <password> ]
    $ sms [ -q | -d ] [ -y ] [ -c <config> ] send
          [ -u <user> ] [ -p <password> ]
          [ -g <gateway> ] [ -r <receiver> ] [ -s <sender> ]
          [ -p <phonebook> ] [ -e ] [ -i ]
          [ <message> ]
    $ sms [ -q | -d ] [ -y ] [ -c <config> ] pb

Because of the way ``options.py`` works, the general program options and
subcommand options can be mixed and can be placed before or after the
subcommand itself. Also, options which are relevant only for ``send`` can be
given when using ``check`` or ``pb`` and will be silently ignored.

Command Line Options
--------------------

Descriptive options :
    ``-h, --help`` :
        Display help and exit.
    ``-v, --version`` :
        Display version number and exit.

General program options :
    ``-q, --quiet`` :
        Silence all output. Useful when executing the script from a cronjob.
    ``-d, --debug`` :
        Activate debugging. Will output noisily what is being done.
    ``-y, --dry-run`` :
        Don't perform any REST calls. Useful in combination with ``[-d |
        --debug]``.
    ``-c, --config <config>`` :
        The config file to use (default ``~/.fullsms``). Useful if you have
        multiple configurations.

For ``send`` and ``check`` subcommands :
    ``-u, --user <user>`` :
        The ``fullsms.de`` username.
    ``-p, --password <password>`` :
        The ``fullsms.de`` password.

For ``check`` only:
    ``-a, --amount`` :
        Output only the amount, no fluff.

For ``send`` only :
    ``-g, --gateway <gateway>`` :
        The gateway to use (default ``22``). ``fullsms.de`` has multiple
    ``-r, --receiver <receiver>`` :
        The person to send the message to.
    ``-s, --sender <sender>`` :
        The sender to use. Can be 11 alphanumeric or 15 numeric characters.

Phonebook management :
    ``-b, --phonebook <phonebook>`` :
        The phonebook file (default: ``~/.fullsms-book``). See below for
        details about this file.
    ``-e, --expand`` :
        Expand sender from the phonebook. This means, that if the sender name
        is found in the phonebook, the corresponding number will be used as a
        sender.
    ``-i, --ignore`` :
        Ignore errors when expanding receiver. The most common use case is to
        send messages to people in your phonebook. To avoid typos, the script
        will abort if the given receiver is not in your phone book. This option
        disables this behaviour. If you wish to disable this b default,
        consider using the config file.

Note: since ``[-e | --expand]``, ``[-i | --ignore]`` and ``[-a | --amount]``
can also be specified in the config file, you may need a way to revert these if
they are set to ``true``. Courtesy of ``options.py`` we have the negation
options ``--no-expand``, ``--no-ignore`` and ``--no-amount`` at no additional
cost which will do exactly that.

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
* ``amount``

The three settings ``expand``, ``ignore`` and ``amount`` are booleans and must
take either the value ``true`` or ``false`` (or any semantically reasonable or
case insensitive equivalent). All others are strings.

Example::

    [settings]
    user      = MaxMusterman
    password  = maxmustermangeheim
    gateway   = 11
    receiver  = 0123456789
    sender    = 0123456789
    phonebook = ~/.mybook
    expand    = true
    ignore    = true

Reminder: If you wish to use an alternative file, use the ``[-c | --config]``
option.

Phonebook
---------

A rudimentary phonebook file is supported. By default, the script searches
``~/.fullsms-book`` for entries in a section titled ``contacts``::

    [contacts]
    max = 0123456789
    maxine = 1234567890
    maximilian = 2345678901

Thus you can use these defined aliases on the command line, see below for
examples. If you want to use a different file, use either the ``phonebook``
option in the config file or the ``[-b | --phonebook]`` command line option.

Example command line usage
--------------------------

The following examples make the assumption that a correct ``user`` and
``password`` are stored in the config file (see above) and that a phonebook
with appropriate entries has been defined.

In the simplest case, only a receiver and message are required::

    $ sms send -r maxine "Hello honey, I'm home"

In this case the phone number of ``maxine`` will be looked up in the phonebook
and expanded. If no such entry exists, the execution will be aborted in order
to save you from typos. If you wish to supply the phone number on the command
line, you need to use the  ``[-i | --ignore]`` option, which will ignore any
errors caused by numbers not in the phone book::

    $ sms send -i -r 0123456789 "Hello honey, I'm home"

If you wish to make this the default behaviour, set ``ignore`` to ``true`` in
your config file.

Using the ``[-e | --expand]`` command-line option to expand the sender from the
phonebook too, the following will send a message to ``maxine`` looking like it
came from ``maximilian``::

    $ sms send -r maxine -e -s maximilian "Any plans for tonight?"

Because the sender can be either 11 alphanumeric or 15 numeric characters, you
need to enable expansion explicitly. Again, If you wish to make this the
default behaviour, set ``expand`` to ``true`` in your config file.  Lastly,
note that setting an arbitrary sender may or may not be supported by the
gateway, see the ``fullsms.de`` documentation for details.

The ``<message>`` is optional, since the ``send`` subcommand also accepts input
on ``stdin``, for example by using a UNIX pipe::

    $ echo "Any plans for tonight?" | sms send -r maxine

Or, if you don't supply something, the script will wait for input, which you
can terminate by sending ``EOF`` (``ctrl+d``)::

    $ sms send -r maxine
    Any plans for tonight? <ctrl+d>

There is also the ``check`` subcommand to check account balance::

    $ sms check
    The current balance for the account 'MaxMusterman' is: 12,571 €

If you want only the amount, use the ``[-a | --amount]`` switch or the
corresponding config file setting::

    $ sms check -a
    12,571

And finally, a ``pb`` subcommand to print the phone-book::

    $ sms pb
    max           : 0123456789
    maximilian    : 2345678901
    maxine        : 1234567890

By convetion, a ``[-h | --help]`` option is provided::

    $ sms -h

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
    (200, '12,571'

TODO
----

* Better format for the option list
* Use BeautifulSoup to get the recent messages

Changelog
---------

* v0.2.0 - XXXX-XX-XX

  * 'pb' subcommand to print the sorted phonebook
  * Fix a bug caused by change in upstream API
    (credit remaining uses ',' now instead of '.')
  * Print the number of chars used when sending
  * Accept messages on stdin

* v0.1.0 - 2012-08-20

  * Initial release
  * 'check' and 'send' subcommands
  * Phone book

Author and Copyright
--------------------

* ``fullsms.py`` is © 2012 Valentin Haenel, under a 2-Clause BSD license
* ``options.py`` is © 2010-2012 Avery Pennarun, under a 2-Clause BSD license

``options.py`` is included verbatim in the file ``fullsms.py`` to make
installation and usage so much easier. The copied code is clearly marked and
the original copyright statement etc. is included as required by the licence.
