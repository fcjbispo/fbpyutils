import pytest
from fbpyutils import string


def test_uuid():
    u = string.uuid()
    assert isinstance(u, str)
    assert len(u) == 36  # UUID padrão tem 36 caracteres


def test_similarity_same_strings():
    sim = string.similarity("hello", "hello")
    assert sim == 1.0


def test_similarity_different_strings():
    sim = string.similarity("hello", "world")
    assert sim < 1.0


def test_similarity_ignore_case():
    sim = string.similarity("Hello", "hello")
    assert sim == 1.0


def test_similarity_compress_spaces():
    sim = string.similarity("hello  world", "hello world")
    assert sim == 1.0


def test_random_string_default_length():
    random_str = string.random_string()
    assert isinstance(random_str, str)
    assert len(random_str) == 32


def test_random_string_custom_length():
    random_str = string.random_string(x=10)
    assert isinstance(random_str, str)
    assert len(random_str) == 10


def test_random_string_no_digits():
    random_str = string.random_string(include_digits=False)
    assert not any(char.isdigit() for char in random_str)


def test_random_string_special_chars():
    random_str = string.random_string(include_special=True)
    assert any(char in "!@#$%^&amp;*_" for char in random_str)


def test_json_string():
    data = {"name": "Test", "value": 123}
    json_str = string.json_string(data)
    assert isinstance(json_str, str)
    assert json_str == '{"name": "Test", "value": 123}'


def test_hash_string():
    hash_str = string.hash_string("test string")
    assert isinstance(hash_str, str)
    assert len(hash_str) == 32  # MD5 hash tem 32 caracteres hexadecimais


def test_hash_json():
    data = {"name": "Test", "value": 123}
    hash_json_str = string.hash_json(data)
    assert isinstance(hash_json_str, str)
    assert len(hash_json_str) == 32  # MD5 hash tem 32 caracteres hexadecimais


def test_normalize_value_default():
    normalized_value = string.normalize_value(1.2)
    assert normalized_value == "120"


def test_normalize_value_custom_size_decimal():
    normalized_value = string.normalize_value(1.234, size=6, decimal_places=3)
    assert normalized_value == "01234"


def test_translate_special_chars():
    translated_string = string.translate_special_chars("áéíóúçãõ")
    assert translated_string == "aeioucao"


def test_normalize_names_default():
    names = ["João Silva", "Maria/Souza", "José  Santos"]
    normalized_names = string.normalize_names(names)
    assert normalized_names == ["joao_silva", "maria_souza", "jose__santos"]


def test_normalize_names_no_specials():
    names = ["João Silva", "Maria/Souza", "José  Santos"]
    normalized_names = string.normalize_names(names, normalize_specials=False)
    assert normalized_names == ["joão_silva", "maria_souza", "josé__santos"]


def test_split_by_lengths_empty_lengths():
    substrings = string.split_by_lengths("HelloWorld", [])
    assert substrings == []


def test_split_by_lengths_valid_lengths():
    substrings = string.split_by_lengths("HelloWorld", [5, 5])
    assert substrings == ["Hello", "World"]


def test_split_by_lengths_long_string():
    long_string = "ThisIsALongStringForTest"
    lengths = [4, 2, 5, 7, 5]
    substrings = string.split_by_lengths(long_string, lengths)
    assert substrings == ["This", "Is", "ALong", "StringF", "orTes"]
