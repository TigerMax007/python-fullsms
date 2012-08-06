#!/usr/bin/env python
# -*- coding: utf-8 -*-

import textwrap
import tempfile

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
