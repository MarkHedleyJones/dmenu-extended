#! /usr/bin/env python
# -*- coding: utf8 -*-

import mock
import pytest
import sys
from os import path

sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )
import dmenu_extended as d

menu = d.dmenu()

def test_required_variables_available():
    assert d.path_cache[-len('dmenu-extended'):] == 'dmenu-extended'

def test_command_to_list():
    assert menu.command_to_list(['a', 'b', 'c']) == [u'a', u'b', u'c']
    assert menu.command_to_list('a b c') == [u'a', u'b', u'c']
    assert menu.command_to_list(['a', 'b c']) == [u'a', u'b', u'c']
    assert menu.command_to_list(['a', 'b', 'c', 'aö']) == [u'a', u'b', u'c', u'a\xf6']
    assert menu.command_to_list('a b c aö') == [u'a', u'b', u'c', u'a\xf6']
    assert menu.command_to_list([u'a', u'b c aö']) == [u'a', u'b', u'c', u'a\xf6']
    assert menu.command_to_list('xdg-open "/home/user/aö/"') == [u'xdg-open', u'/home/user/a\xf6/']
    assert menu.command_to_list('xdg-open /home/user/aö/') == [u'xdg-open', u'/home/user/a\xf6/']
    assert menu.command_to_list('xdg-open "/home/user/aö/filename"') == [u'xdg-open', u'/home/user/a\xf6/filename']
    assert menu.command_to_list('xdg-open "/home/user/aö/file name"') == [u'xdg-open', u'/home/user/a\xf6/file name']
    assert menu.command_to_list('xdg-open /home/user/aö/filename') == [u'xdg-open', u'/home/user/a\xf6/filename']
    assert menu.command_to_list('xdg-open /home/user/aö/file name') == [u'xdg-open', u'/home/user/a\xf6/file', 'name']
    assert menu.command_to_list('xdg-open "/home/user/aö/foldername/"') == [u'xdg-open', u'/home/user/a\xf6/foldername/']
    assert menu.command_to_list('xdg-open "/home/user/aö/folder name/"') == [u'xdg-open', u'/home/user/a\xf6/folder name/']
    assert menu.command_to_list('xdg-open /home/user/aö/folder name/') == [u'xdg-open', u'/home/user/a\xf6/folder', 'name/']
    assert menu.command_to_list('xdg-open /home/user/aö/foldername/') == [u'xdg-open', u'/home/user/a\xf6/foldername/']
    assert menu.command_to_list('xdg-open "/home/user/aö/"foldernam "e/"') == [u'xdg-open', u'/home/user/a\xf6/foldernam', u'e/']
    assert menu.command_to_list('xdg-open "/home/user/1983 - BVerfG - Volkszahlungsurteil - 1983.pdf"') == [u'xdg-open', u'/home/user/1983 - BVerfG - Volkszahlungsurteil - 1983.pdf']


def test_scan_binaries_file_in_system_path():
    with mock.patch.object(menu, 'system_path', new=lambda: [u'/bin', u'/bin/cp'] ):
        assert type(menu.scan_binaries()) == list
