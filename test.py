#!/usr/bin/env python
# -*- coding: utf-8 -*-

import textwrap
import tempfile
from ConfigParser import NoSectionError

import nose.tools as nt

import fullsms as sms

def test_parse_config():
    # first test that it works as intended
    test_config = textwrap.dedent("""
    [settings]
    user     = MaxMusterman
    password = maxmustermangeheim
    gateway  = 11
    sender   = 0123456789
    receiver = 0123456789
    """)
    config_file = tempfile.NamedTemporaryFile()
    config_filename = config_file.name
    config_file.writelines(test_config)
    config_file.flush()
    config = sms.parse_config(config_filename=config_filename)
    expected = {'user': 'MaxMusterman',
                'password': 'maxmustermangeheim',
                'gateway': '11',
                'sender': '0123456789',
                'receiver': '0123456789'}
    nt.assert_equal(config, expected)
    nt.assert_raises(IOError, sms.parse_config, config_filename="nofile")
    test_config_section = textwrap.dedent("""
    [configuration]
    user     = MaxMusterman
    password = maxmustermangeheim
    gateway  = 11
    sender   = 0123456789
    receiver = 0123456789
    """)
    config_file = tempfile.NamedTemporaryFile()
    config_filename = config_file.name
    config_file.writelines(test_config_section)
    config_file.flush()
    nt.assert_raises(NoSectionError, sms.parse_config,
            config_filename=config_filename)
    config = sms.parse_config(section='configuration',
            config_filename=config_filename)
    nt.assert_equal(config, expected)
