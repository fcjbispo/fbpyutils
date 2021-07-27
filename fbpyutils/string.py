'''
Several functions to manipulate and processes strings and/or
produce strings from any kind of data.
'''
import random
import string
import hashlib
import json

from datetime import datetime
from difflib import SequenceMatcher

import uuid as u

from typing import Dict


_ACCENTED_CHARS = ''
for c in 'áãâäàéèëêíìîïóòõôöúùûüçñ':
    _ACCENTED_CHARS += c + c.upper()

_NORMALIZED_CHARS = ''
for c in 'aaaaaeeeeiiiiooooouuuucn':
    _NORMALIZED_CHARS += c + c.upper()

_TRANSLATION_TAB = {}
for i in range(len(_ACCENTED_CHARS)):
    _TRANSLATION_TAB[ord(_ACCENTED_CHARS[i])] = _NORMALIZED_CHARS[i]


def uuid() -> str:
    '''
    Generates a standard uuid4 as string

        Return a string with a standard uuid key
    '''
    return u.uuid4().__str__()


def similarity(
    x: str,
    y: str,
    ignore_case: bool = True,
    compress_spaces: bool = True
) -> float:
    '''
    Calculates the similarity ratio between two strings.
    The result is in a range from 0 to 1 where 1 means both strings are equal

        x
            The first string to compare
        y
            The second string to be compared with
        ignore_case
            If True ignores the strings case. Default=True
        compress_spaces
            If True remove extra space sequences in the strings. Default=True

        Return the similarity ratio between the strings in a range from 0 to 1
        where 1 means that both strings are equal
    '''
    def compress(z: str) -> str:
        while "  " in z:
            z = z.replace("  ", " ")
        return z

    if ignore_case:
        x = x.lower()
        y = y.lower()

    if compress_spaces:
        x = compress(x)
        y = compress(y)

    return SequenceMatcher(None, x, y).ratio()


def random_string(
    x: int = 32,
    include_digits: bool = True,
    include_special: bool = False
) -> str:
    '''
    Generates a random string with the combination of lowercase and uppercase
    letters and optionally digits and special characters

        x
            Set the random string's lenght. Default=24
        include_digits
            If True, include random digits on the generated string.
            Default=True
        include_special
            If True, include special characteres on the generated string.
            Default=False

        Return a random string with the specified lenght with or without
        digits or special characters
    '''
    letters = string.ascii_letters + \
        (string.digits if include_digits else '') + \
        ('!@#$%^&*_' if include_special else '')
    return ''.join(random.choice(letters) for i in range(x))


def json_string(x: Dict) -> str:
    '''
    Converts a dict to string encoded as utf-8
        x
            The dict to be converted

        Return a string version of the dictionary encoded as utf-8
    '''
    _default = lambda x: x.__str__()
    s = json.dumps(
        x, default=_default,
        ensure_ascii=False).encode('utf8')

    return s.decode()


def hash_string(x: str) -> str:
    '''
    Generates an hexadecimal hash string from x using MD5 algorithm
        x
            The source string to be used to create the hash

        Return a MD5 hash string created from x
    '''
    return hashlib.md5(x.encode('utf-8')).hexdigest()


def hash_json(x: Dict) -> str:
    '''
    Generates an hexadecimal hash string from x using MD5 algorithm
        x
            A dict to be used to create the hash

        Return a MD5 hash string created from x
    '''
    return hash_string(json_string(x))


def normalize_value(
    x: float, size: int = 4, decimal_places: int = 2
) -> str:
    '''
    Converts a float number into a string formatted with padding zeroes
    for the fixed lenght and decimal places
        x
            The float number to convert
        size
            The lenght of the result string. Default = 4
        decimal_places
            Number of zeroes to fill in the decimal places. Default = 2

        Return a fixed lenght string with zeroes padding on left and right
            Ex.:
                normalize_amount(1.2, size=5, decimal_places=2)
                will produce 00120

                normalize_amount(1.21, size=5, decimal_places=2)
                will produce 00121

                normalize_amount(12.3) will produce 1230
    '''
    vl = str(int(abs(x)*(10**decimal_places)))
    return vl.rjust(size, '0') if len(vl) < size else vl


def translate_accented_word(x) -> str:
    '''
    Translates accented word in non accented word
        x
            The word to be translated
        Return a new word with all accented chars translated to
            non-accented ones
    '''
    x = x or ''

    return x.translate(_TRANSLATION_TAB)