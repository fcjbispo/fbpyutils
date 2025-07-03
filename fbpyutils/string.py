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

from fbpyutils import logging


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
    generated_uuid = str(u.uuid4())
    logging.Logger.debug(f"Generated UUID: {generated_uuid}")
    return generated_uuid


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
    logging.Logger.debug(f"Calculating similarity between '{x}' and '{y}' (ignore_case: {ignore_case}, compress_spaces: {compress_spaces})")
    def compress(z: str) -> str:
        original_z = z
        while "  " in z:
            z = z.replace("  ", " ")
        if original_z != z:
            logging.Logger.debug(f"Compressed spaces: '{original_z}' -> '{z}'")
        return z

    if ignore_case:
        x = x.lower()
        y = y.lower()
        logging.Logger.debug(f"Strings after lowercasing: x='{x}', y='{y}'")

    if compress_spaces:
        x = compress(x)
        y = compress(y)

    ratio = SequenceMatcher(None, x, y).ratio()
    logging.Logger.debug(f"Similarity ratio: {ratio}")
    return ratio


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
    logging.Logger.debug(f"Generating random string of length {x} (include_digits: {include_digits}, include_special: {include_special})")
    letters = string.ascii_letters + \
        (string.digits if include_digits else '') + \
        ('!@#$%^&*_' if include_special else '')
    
    if not letters:
        logging.Logger.warning("No character set selected for random string generation. Returning empty string.")
        return ""

    generated_string = ''.join(random.choice(letters) for i in range(x))
    logging.Logger.debug(f"Generated random string (first 5 chars): {generated_string[:5]}...")
    return generated_string


def json_string(x: Dict) -> str:
    """
    Converts a dictionary to a string encoded as UTF-8.
     Args:
        x (Dict): The dictionary to be converted.
     Returns:
        str: A string version of the dictionary encoded as UTF-8.
    """
    logging.Logger.debug("Converting dictionary to JSON string.")
    _default = lambda obj: obj.__str__() # Use obj instead of x to avoid shadowing
    try:
        s = json.dumps(
            x, default=_default,
            ensure_ascii=False).encode('utf8')
        decoded_string = s.decode()
        logging.Logger.debug("Successfully converted dictionary to JSON string.")
        return decoded_string
    except TypeError as e:
        logging.Logger.error(f"TypeError during JSON string conversion: {e}. Input: {x}")
        raise
    except Exception as e:
        logging.Logger.error(f"An unexpected error occurred during JSON string conversion: {e}. Input: {x}")
        raise


def hash_string(x: str) -> str:
    """
    Generates a hexadecimal hash string from x using the MD5 algorithm.
     Args:
        x (str): The source string to be used to create the hash.
     Returns:
        str: An MD5 hash string created from x.
    """
    logging.Logger.debug(f"Hashing string (first 10 chars): '{x[:10]}...'")
    hashed_string = hashlib.md5(x.encode('utf-8')).hexdigest()
    logging.Logger.debug(f"Generated hash: {hashed_string}")
    return hashed_string


def hash_json(x: Dict) -> str:
    """
    Generates a hexadecimal hash string from a dictionary x using the MD5 algorithm.
     Args:
        x (Dict): A dictionary to be used to create the hash.
     Returns:
        str: An MD5 hash string created from x.
    """
    logging.Logger.debug("Hashing JSON dictionary.")
    hashed_json = hash_string(json_string(x))
    logging.Logger.debug(f"Generated JSON hash: {hashed_json}")
    return hashed_json


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
    logging.Logger.debug(f"Normalizing value {x} to string (size: {size}, decimal_places: {decimal_places})")
    try:
        format_string = "{:0" + str(size) + "." + str(decimal_places) + "f}"
        normalized_string = format_string.format(abs(x)).replace('.', '')
        logging.Logger.debug(f"Normalized string: {normalized_string}")
        return normalized_string
    except ValueError as e:
        logging.Logger.error(f"ValueError during value normalization: {e}. Input: {x}, size: {size}, decimal_places: {decimal_places}")
        raise
    except Exception as e:
        logging.Logger.error(f"An unexpected error occurred during value normalization: {e}. Input: {x}")
        raise


def translate_special_chars(x: str) -> str:
    """
    Translates special (accented) characters in a string to regular characters.
     Args:
        x (str): The string to be translated.
     Returns:
        str: A new string with all special characters translated to regular ones.
    """
    logging.Logger.debug(f"Translating special characters for string: '{x}'")
    x = x or ''
    translated_string = x.translate(_TRANSLATION_TAB)
    logging.Logger.debug(f"Translated string: '{translated_string}'")
    return translated_string


from typing import List


def normalize_names(names: List[str], normalize_specials: bool = True) -> List[str]:
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
    logging.Logger.debug(f"Normalizing names (normalize_specials: {normalize_specials}). Input names: {names}")
    normalized_list = [
        str(translate_special_chars(c) if normalize_specials else c).replace(' ', '_').replace('/', '_').lower() for c in names
    ]
    logging.Logger.debug(f"Normalized names: {normalized_list}")
    return normalized_list


def split_by_lengths(string: str, lengths: List[int]) -> List[str]:
    """
    Splits a given string into multiple substrings based on the provided lengths.

    Args:
        string (str): The input string to be split.
        lengths (list): A list of integers representing the desired lengths of the substrings.

    Returns:
        list: A list of substrings obtained by splitting the input string based on the provided lengths.

    Raises:
        None

    Example:
        >>> split_by_lengths("HelloWorld", [5, 5])
        ['Hello', 'World']
    """
    logging.Logger.debug(f"Splitting string by lengths. Input string length: {len(string)}, lengths: {lengths}")
    substrings = []
    start_index = 0
    for i, length in enumerate(lengths):
        end_index = start_index + length
        substring = string[start_index:end_index]
        if substring:  # Adiciona apenas se não for vazio
            substrings.append(substring)
            logging.Logger.debug(f"Added substring {i+1}: '{substring}'")
        else:
            logging.Logger.warning(f"Substring {i+1} is empty for length {length} at index {start_index}. Skipping.")
        start_index = end_index
    logging.Logger.debug(f"Finished splitting string. Total substrings: {len(substrings)}")
    return substrings
