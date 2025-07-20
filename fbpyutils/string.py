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
    """Generate a standard UUID4 string.

    Returns:
        A string with a standard UUID key.
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
    """Calculate the similarity ratio between two strings.

    The result is a float between 0 and 1, where 1.0 means the strings are
    identical.

    Args:
        x: The first string to compare.
        y: The second string to compare.
        ignore_case: If True, ignores case during comparison.
        compress_spaces: If True, removes extra space sequences.

    Returns:
        The similarity ratio (0.0 to 1.0).
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
    """Generate a random string.

    Combines lowercase and uppercase letters, and optionally digits and
    special characters.

    Args:
        x: The length of the random string.
        include_digits: If True, includes digits (0-9).
        include_special: If True, includes special characters (!@#$%^&*_).

    Returns:
        A random string with the specified properties.
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
    """Convert a dictionary to a JSON string.

    The output string is encoded as UTF-8.

    Args:
        x: The dictionary to convert.

    Returns:
        A JSON string representation of the dictionary.
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
    """Generate an MD5 hash from a string.

    The input string is encoded as UTF-8 before hashing.

    Args:
        x: The string to hash.

    Returns:
        A hexadecimal MD5 hash string.
    """
    logging.Logger.debug(f"Hashing string (first 10 chars): '{x[:10]}...'")
    hashed_string = hashlib.md5(x.encode('utf-8')).hexdigest()
    logging.Logger.debug(f"Generated hash: {hashed_string}")
    return hashed_string


def hash_json(x: Dict) -> str:
    """Generate an MD5 hash from a dictionary.

    The dictionary is first converted to a JSON string, then hashed.

    Args:
        x: The dictionary to hash.

    Returns:
        A hexadecimal MD5 hash string.
    """
    logging.Logger.debug("Hashing JSON dictionary.")
    hashed_json = hash_string(json_string(x))
    logging.Logger.debug(f"Generated JSON hash: {hashed_json}")
    return hashed_json


def normalize_value(
    x: float, size: int = 4, decimal_places: int = 2
) -> str:
    """Convert a float to a zero-padded string.

    Formats a float into a string of a fixed length, with zero-padding
    for both the integer and decimal parts.

    Args:
        x: The float number to convert.
        size: The total length of the output string.
        decimal_places: The number of decimal places to include.

    Returns:
        A fixed-length string with left and right zero-padding.

    Example:
        >>> normalize_value(1.2, size=5, decimal_places=2)
        '00120'
        >>> normalize_value(1.21, size=5, decimal_places=2)
        '00121'
        >>> normalize_value(12.3)
        '1230'
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
    """Translate special (accented) characters to their basic counterparts.

    Args:
        x: The string to translate.

    Returns:
        A new string with special characters replaced.
    """
    logging.Logger.debug(f"Translating special characters for string: '{x}'")
    x = x or ''
    translated_string = x.translate(_TRANSLATION_TAB)
    logging.Logger.debug(f"Translated string: '{translated_string}'")
    return translated_string


from typing import List


def normalize_names(names: List[str], normalize_specials: bool = True) -> List[str]:
    """Normalize a list of strings to a consistent format.

    Converts to lowercase, replaces spaces and slashes with underscores,
    and optionally translates special characters.

    Args:
        names: The list of strings to normalize.
        normalize_specials: If True, translates special characters.

    Returns:
        A list of normalized strings.
    """
    logging.Logger.debug(f"Normalizing names (normalize_specials: {normalize_specials}). Input names: {names}")
    normalized_list = [
        str(translate_special_chars(c) if normalize_specials else c).replace(' ', '_').replace('/', '_').lower() for c in names
    ]
    logging.Logger.debug(f"Normalized names: {normalized_list}")
    return normalized_list


def split_by_lengths(string: str, lengths: List[int]) -> List[str]:
    """Split a string into substrings of specified lengths.

    Args:
        string: The input string to split.
        lengths: A list of integers representing the lengths of the
            substrings.

    Returns:
        A list of substrings.

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
