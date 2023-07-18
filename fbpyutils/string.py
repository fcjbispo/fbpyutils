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


_SPECIAL_CHARS = ''.join([
    c + c.upper() for c in 'áãâäàéèëêíìîïóòõôöúùûüçñ'
])

_NORMALIZED_CHARS = ''.join([
    c + c.upper() for c in 'aaaaaeeeeiiiiooooouuuucn'
])

_TRANSLATION_TAB = {}
for i in range(len(_SPECIAL_CHARS)):
    _TRANSLATION_TAB[ord(_SPECIAL_CHARS[i])] = _NORMALIZED_CHARS[i]


def uuid() -> str:
    """
    Generates a standard uuid4 as string.
     Returns:
        str: A string with a standard uuid key.
    """
    return u.uuid4().__str__()


def similarity(
    x: str,
    y: str,
    ignore_case: bool = True,
    compress_spaces: bool = True
) -> float:
    """
    Calculates the similarity ratio between two strings.
    The result is in a range from 0 to 1 where 1 means both strings are equal.
     Args:
        x (str): The first string to compare.
        y (str): The second string to be compared with.
        ignore_case (bool, optional): If True, ignores the strings case. Default is True.
        compress_spaces (bool, optional): If True, removes extra space sequences in the strings. Default is True.
     Returns:
        float: The similarity ratio between the strings in a range from 0 to 1
            where 1 means that both strings are equal.
    """
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
    """
    Generates a random string with the combination of lowercase and uppercase
    letters and optionally digits and special characters.
     Args:
        x (int, optional): Set the random string's length. Default is 32.
        include_digits (bool, optional): If True, include random digits in the generated string.
            Default is True.
        include_special (bool, optional): If True, include special characters in the generated string.
            Default is False.
     Returns:
        str: A random string with the specified length, with or without digits or special characters.
    """
    letters = string.ascii_letters + \
        (string.digits if include_digits else '') + \
        ('!@#$%^&*_' if include_special else '')
    return ''.join(random.choice(letters) for i in range(x))


def json_string(x: Dict) -> str:
    """
    Converts a dictionary to a string encoded as UTF-8.
     Args:
        x (Dict): The dictionary to be converted.
     Returns:
        str: A string version of the dictionary encoded as UTF-8.
    """
    _default = lambda x: x.__str__()
    s = json.dumps(
        x, default=_default,
        ensure_ascii=False).encode('utf8')

    return s.decode()


def hash_string(x: str) -> str:
    """
    Generates a hexadecimal hash string from x using the MD5 algorithm.
     Args:
        x (str): The source string to be used to create the hash.
     Returns:
        str: An MD5 hash string created from x.
    """
    return hashlib.md5(x.encode('utf-8')).hexdigest()


def hash_json(x: Dict) -> str:
    """
    Generates a hexadecimal hash string from a dictionary x using the MD5 algorithm.
     Args:
        x (Dict): A dictionary to be used to create the hash.
     Returns:
        str: An MD5 hash string created from x.
    """
    return hash_string(json_string(x))


def normalize_value(
    x: float, size: int = 4, decimal_places: int = 2
) -> str:
    """
    Converts a float number into a string formatted with padding zeroes
    for the fixed length and decimal places.
     Args:
        x (float): The float number to convert.
        size (int, optional): The length of the result string. Default is 4.
        decimal_places (int, optional): Number of zeroes to fill in the decimal places. Default is 2.
     Returns:
        str: A fixed length string with zeroes padding on left and right.
     Example:
        normalize_value(1.2, size=5, decimal_places=2)
        will produce '00120'
         normalize_value(1.21, size=5, decimal_places=2)
        will produce '00121'
         normalize_value(12.3)
        will produce '1230'
    """
    vl = str(int(abs(x)*(10**decimal_places)))
    return vl.rjust(size, '0') if len(vl) < size else vl


def translate_special_chars(x) -> str:
    """
    Translates special (accented) characters in a string to regular characters.
     Args:
        x (str): The string to be translated.
     Returns:
        str: A new string with all special characters translated to regular ones.
    """
    x = x or ''

    return x.translate(_TRANSLATION_TAB)


def normalize_names(names, normalize_specials=True):
    """
    Normalize string names to lower case, with spaces and slashes converted to underscores,
    and special characters translated.
     Args:
        names (list): The list of strings to be normalized.
        normalize_specials (bool, optional): If True, translates special characters into their regular ones.
            Default is True.
     Returns:
        list: The list of string names normalized.
    """
    return [
        str(translate_special_chars(c) if normalize_specials else c).replace(' ', '_').replace('/', '_').lower() for c in names
    ]