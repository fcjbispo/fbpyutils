import os
import pytest


_BASE_PATH = os.path.sep.join(
    os.path.abspath(__file__).split(os.path.sep)[:-1]
)


@pytest.fixture(scope='session', autouse=True)
def resources_path():
   return os.path.sep.join([_BASE_PATH, 'resources'])


@pytest.fixture(scope='session', autouse=True)
def expected_files():
   return [
      os.path.sep.join([_BASE_PATH, 'resources', 'file1.txt']),
      os.path.sep.join([_BASE_PATH, 'resources', 'file2.txt']),
      os.path.sep.join([_BASE_PATH, 'resources', 'pasta1', 'file3.csv'])
   ]

