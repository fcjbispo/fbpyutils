import os
import pytest

from fbpyutils import file as FU, xlsx as XL

def setup_module(module):
    global root_dir, resources_dir
    root_dir = FU.absolute_path(__file__)
    resources_dir = os.path.sep.join([root_dir, 'resources'])
    print(f"*** SETUP DONE ***")

def teardown_module(module):
    print(f"*** TEARDOWN DONE ***")

def test_load_empty_file():
    assert False

def test_load_non_existent_file():
    assert False

def test_load_xls_file():
    assert False

def test_load_xlsx_file():
    assert False
