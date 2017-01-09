# -*- coding: utf-8 -*-
import subprocess
import sys

# This should be written as a proper test (framework?) to use the
# command_to_list function in-place instead.

def command_to_list(command):
    """
    Takes any combination of strings and lists and flattens into a list of
    strings. Also handles lists that contain stinrgs that contain spaces.
    """
    out = []
    if type(command) == list:
        tmp = []
        for i, item in enumerate(command):
            if item.find(' ') != -1:
                tmp = tmp + item.split(' ')
            else:
                tmp =  tmp + [item]
        out = tmp
    elif type(command) == str or type(command) == unicode:
        out = command.split(' ')

    quote_count = "".join(out).count('"')
    if quote_count > 0 and quote_count % 2 == 0:
        # Bring split parts that were enclosed by quotes back together
        restart = 1
        while restart:
            restart = 0
            for index, part in enumerate(out):
                if part.count('"') % 2 != 0 and index + 1 <= len(out) - 1:
                    out[index] = out[index] + ' ' + out[index+1]
                    del(out[index+1])
                    restart = 1
                    break
        for index, part in enumerate(out):
            out[index] = part.replace('"', '')
    return out

tests = [
    (['a', 'b', 'c'], ['a', 'b', 'c']),
    ('a b c', ['a', 'b', 'c']),
    (['a', 'b c'], ['a', 'b', 'c']),
    (['a', 'b', 'c', 'aö'], ['a', 'b', 'c', 'aö']),
    ('a b c aö', ['a', 'b', 'c', 'aö']),
    (['a', 'b c aö'], ['a', 'b', 'c', 'aö']),
    ('xdg-open "/home/user/aö/"', ['xdg-open', '/home/user/a\xc3\xb6/']),
    ('xdg-open /home/user/aö/', ['xdg-open', '/home/user/a\xc3\xb6/']),
    ('xdg-open "/home/user/aö/filename"', ['xdg-open', '/home/user/a\xc3\xb6/filename']),
    ('xdg-open "/home/user/aö/file name"', ['xdg-open', '/home/user/a\xc3\xb6/file name']),
    ('xdg-open /home/user/aö/filename', ['xdg-open', '/home/user/a\xc3\xb6/filename']),
    ('xdg-open /home/user/aö/file name', ['xdg-open', '/home/user/a\xc3\xb6/file', 'name']),
    ('xdg-open "/home/user/aö/foldername/"', ['xdg-open', '/home/user/a\xc3\xb6/foldername/']),
    ('xdg-open "/home/user/aö/folder name/"', ['xdg-open', '/home/user/a\xc3\xb6/folder name/']),
    ('xdg-open /home/user/aö/folder name/', ['xdg-open', '/home/user/a\xc3\xb6/folder', 'name/']),
    ('xdg-open /home/user/aö/foldername/', ['xdg-open', '/home/user/a\xc3\xb6/foldername/']),
    ('xdg-open "/home/user/aö/"foldernam "e/"', ['xdg-open', '/home/user/a\xc3\xb6/foldernam', 'e/']),
    ('xdg-open "/home/mark/1983 - BVerfG - Volkszahlungsurteil - 1983.pdf"', ['xdg-open', '/home/mark/1983 - BVerfG - Volkszahlungsurteil - 1983.pdf'])
]

for test, correct in tests:
    if command_to_list(test) != correct:
        print("FAIL\t"),
        print(test),
        print(' -> '),
        print(command_to_list(test)),
        print(' != '),
        print(repr(correct))
    else:
        print("PASS")