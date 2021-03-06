#!/usr/bin/env python
# -*- coding: utf-8 -*-

import textwrap
import tempfile
from ConfigParser import NoSectionError
import StringIO

import nose.tools as nt

import fullsms as sms

def make_tempfile(text):
    """ Utility for creating tempfiles. """
    config_file = tempfile.TemporaryFile()
    config_file.writelines(text)
    config_file.flush()
    config_file.seek(0)
    return config_file

def test_open_config():
    nt.assert_raises(IOError, sms.open_config, "filedoesnotexist")

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
    config_file = make_tempfile(test_config)
    config = sms.parse_config(config_file)
    expected = {'user': 'MaxMusterman',
                'password': 'maxmustermangeheim',
                'gateway': '11',
                'sender': '0123456789',
                'receiver': '0123456789'}
    nt.assert_equal(config, expected)
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
    nt.assert_raises(NoSectionError, sms.parse_config, config_file)
    config_file.seek(0)
    config = sms.parse_config(config_file, section='configuration')
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
    nt.assert_raises(sms.UnknownSettingError, sms.parse_config,
            config_file)
    test_bools = textwrap.dedent("""
    [settings]
    expand = true
    ignore = false
    """)
    config_file = make_tempfile(test_bools)
    expected = {'ignore': False, 'expand': True}
    nt.assert_equal(sms.parse_config(config_file), expected)


def test_parse_phonebook():
    test_phonebook = textwrap.dedent("""
    [contacts]
    max = 0123456789
    maxine = 1234567890
    maximilian = 2345678901
    """)
    phonebook_fp = StringIO.StringIO(test_phonebook)
    contacts = sms.parse_phonebook(phonebook_fp)
    expected = {'max': '0123456789',
                'maxine': '1234567890',
                'maximilian': '2345678901'}
    nt.assert_equal(contacts, expected)
