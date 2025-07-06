import pytest
import fbpyutils

@pytest.fixture(autouse=True)
def setup_fbpyutils():
    """
    A pytest fixture that automatically initializes the fbpyutils library
    before each test function runs. This ensures that the environment and
    logger are configured, preventing `RuntimeError` for tests that
-   depend on them.
    """
    fbpyutils.setup()
