#!/usr/bin/env python
# -*- coding: utf-8 -*-

import textwrap
import tempfile
from ConfigParser import NoSectionError

import nose.tools as nt

import fullsms as sms

def test_parse_config():

    def make_tempfile(text):
        """ Utility for creating tempfiles. """
        config_file = tempfile.NamedTemporaryFile()
        config_file.writelines(text)
        config_file.flush()
        return config_file

    # first test that it works as intended
    test_config = textwrap.dedent("""
    [settings]
    user     = MaxMusterman
    password = maxmustermangeheim
    gateway  = 11
    sender   = 0123456789
    receiver = 0123456789
    """)
    config_file = make_tempfile(test_config)
    config = sms.parse_config(config_filename=config_file.name)
    expected = {'user': 'MaxMusterman',
                'password': 'maxmustermangeheim',
                'gateway': '11',
                'sender': '0123456789',
                'receiver': '0123456789'}
    nt.assert_equal(config, expected)
    nt.assert_raises(IOError, sms.parse_config, config_filename="nofile")
    # check for alternative section name success and failure
    test_config_section = textwrap.dedent("""
    [configuration]
    user     = MaxMusterman
    password = maxmustermangeheim
    gateway  = 11
    sender   = 0123456789
    receiver = 0123456789
    """)
    config_file = make_tempfile(test_config_section)
    nt.assert_raises(NoSectionError, sms.parse_config,
            config_filename=config_file.name)
    config = sms.parse_config(section='configuration',
            config_filename=config_file.name)
    nt.assert_equal(config, expected)
    # check for invalid setting
    test_config_bogus = textwrap.dedent("""
    [settings]
    user     = MaxMusterman
    password = maxmustermangeheim
    gateway  = 11
    sender   = 0123456789
    receiver = 0123456789
    bogus    = nonsense
    """)
    config_file = make_tempfile(test_config_bogus)
    nt.assert_raises(sms.UnknowenSettingError, sms.parse_config,
            config_filename=config_file.name)
