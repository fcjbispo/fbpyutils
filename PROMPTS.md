## SOMETHING WEIRD
I have this python code that runs unit tests. 
```python
import pytest
from fbpyutils import ofx
from datetime import datetime
from unittest import mock
import sys
import json

@mock.patch("builtins.print")
@mock.patch("sys.exit")
@mock.patch("fbpyutils.ofx.read_from_path")
@mock.patch("fbpyutils.ofx.path.exists")
def test_main_valid_file(mock_path_exists, mock_read_from_path, mock_sys_exit, mock_print):
    mock_path_exists.return_value = True
    test_data = {"id": "123"}
    mock_read_from_path.return_value = test_data
    ofx.main(sys.argv[1:])
    mock_print.assert_called_with(json.dumps(test_data, sort_keys=True, indent=4))
    mock_sys_exit.assert_called_with(0)

@mock.patch("builtins.print")
@mock.patch("sys.exit")
@mock.patch("sys.argv", ["ofx.py"])
def test_main_no_arguments(mock_argv_param, mock_exit_param, mock_print_param):
    ofx.main(mock_argv_param[1:])
    mock_print_param.assert_called_with('Use ofx.py --print <file_path>')
    mock_exit_param.assert_called_with(2)
```

The first test runs ok but the second one fails with the following error:
tests/test_ofx_ofx.py::test_main_no_arguments ERROR                                                                                                                                                                                                                                                                                                [100%] 

======================================================================================================================================================================== ERRORS ========================================================================================================================================================================= 
_______________________________________________________________________________________________________________________________________________________ ERROR at setup of test_main_no_arguments ________________________________________________________________________________________________________________________________________________________ 
file d:\Repos\FBPyUtils\tests\test_ofx_ofx.py, line 300
  @mock.patch("builtins.print")
  @mock.patch("sys.exit")
  @mock.patch("sys.argv", ["ofx.py"])
  def test_main_no_arguments(mock_argv_param, mock_exit_param, mock_print_param):
E       fixture 'mock_print_param' not found
>       available fixtures: cache, capfd, capfdbinary, caplog, capsys, capsysbinary, class_mocker, cov, doctest_namespace, mocker, module_mocker, monkeypatch, no_cover, package_mocker, pytestconfig, record_property, record_testsuite_property, record_xml_attribute, recwarn, session_mocker, tmp_path, tmp_path_factory, tmpdir, tmpdir_factory      
>       use 'pytest --fixtures [testpath]' for help on them.

d:\Repos\FBPyUtils\tests\test_ofx_ofx.py:300
================================================================================================================================================================ short test summary info ================================================================================================================================================================ 
ERROR tests/test_ofx_ofx.py::test_main_no_arguments
=================================================================================================================================================================== 1 error in 0.10s ==================================================================================================================================================================== 
PS D:\Repos\FBPyUtils> 


What is wrong? Please fix the bad code.

## APPLY FIX SUGGESTIONS
I applied the following suggestions to fix the code. Please consider these suggestions for your future code reviews:

🧠 What changed and why?
Use monkeypatch or patch.object(sys, 'argv', …) instead of @patch("sys.argv", …).
That decorator won’t wire up parameters correctly in pytest, leading to "fixture not found" issues 

Don't decorate with @mock.patch("sys.argv", …).
That fails because pytest expects parameters in the function signature for each patch decorator—but you passed none, so pytest looks for fixtures.

Use context managers (with mock.patch(...)) instead.
Cleaner, more explicit scope. No parameter misalignments or binding issues.

Call ofx.main(sys.argv[1:]).
For no-argument case, passing [], consistent with test intention.

✅ Summary
Use monkeypatch.setattr(sys, "argv", ["script"]) or patch.object to simulate CLI arguments.

Apply mock.patch via context managers in pytest, unless mixing with fixtures carefully.

Avoid decorator patching of sys.argv when not accepting parameters in test signature.
