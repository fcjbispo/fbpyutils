
## FIX RELEASE V1.6.5
Estou com problemas no clientes da biblioteca fbpyutils.file especificamente com a função `mime_type` que não está sendo executada corretamente devido a problemas com a biblioteca `magic`.

Refatore a biblioteca `fbpyutils` para modernizar a detecção de tipos de arquivo, seguindo estas diretrizes:

1.  **Objetivo Principal:** Substitua toda a lógica customizada de identificação de MIME types pela biblioteca padrão do Python, `mimetypes`.
2.  **Análise:** Identifique as funções em `fbpyutils` que determinam o tipo de um arquivo (MIME type) com base em seu nome ou extensão.
3.  **Implementação:** Em cada local identificado, substitua a lógica existente por uma chamada à função `mimetypes.guess_type(caminho_do_arquivo)`.
4.  **Tratamento do Retorno:** A função `guess_type` retorna uma tupla `(type, encoding)`. Utilize o primeiro elemento (o tipo). Se o tipo retornado for `None`, sua implementação deve retornar um valor padrão seguro, como `'application/octet-stream'`.
5.  **Limpeza:** Remova quaisquer importações, dependências ou código de suporte que se tornaram obsoletos com esta alteração.

*Utilize as orientações de VIBE CODING para realização das tarefas;
*A branch atual do projeto já é a v1.6.5. Utilize-a para manter o repositório de código e realizar o build;
*Atualize o arquivo do projeto `pyproject.toml` com as alterações necessárias;
*Após todo desenvolvimento, testes e aprovação do código, execute o prompt APPLY_CHECKPOINT.


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

## THE GLOBAL LOGGING SYSTEM
Considere as seguintes diretivas para o sistema global de logging a fim de evitar o problema de referência circular ao importar logging diretamente em __init__.py:
- Utilizar um arquivo .json para a configuração da aplicação (app.json) a ser criado na raiz do projeto e cujo dicionário deverá ser passado quando da configuração do sistema global de logging.
- A classe Env em __init__.py deverá também receber este dicionário lido do arquivo app.json como parâmetro para seu construtor e configurar seus valores conforme a seguir:
    - APP: seus valores deverão ser lidos do dicionário recebido como parâmetro.
    - USER_FOLDER e USER_APP_FOLDER deverão ser construídos conforme o código atual.
    - As demais deverão seguir a precedência: variável de ambiente, valor lido do dicionário, valor padrão.
    - A instanciação da classe Env deverá cuidar da verificação e criação de USER_APP_FOLDER.
- A classe Logger DEVERÁ SER MOVIDA para logging.py e deverá ser instanciada com o dicionário lido do arquivo app.json e configurar o sistema global de logging conforme o código a ser implementado e prover a partir dele suas funcionalidades.


## UPDATE ON THE PLAN FOR RELEASE V1.6.3

Consider this snipped code below and perform the following actions:

```python
import os
import base64
import requests

def get_base64_data_from(file_uri: str, timeout: int = 300) -> str:
    # Check if the data file is a local file
    if os.path.exists(file_uri):
        with open(file_uri, "rb") as img_file:
            image_bytes = img_file.read()
        base64_data = base64.b64encode(image_bytes).decode("utf-8")
    # If the data_file is a remote URL
    elif file_uri.startswith("http://") or file_uri.startswith("https://"):
        try:
            response = requests.get(file_uri, timeout=timeout)
            response.raise_for_status()
            image_bytes = response.content
            base64_data = base64.b64encode(image_bytes).decode("utf-8")
        except Exception as e:
            print(f"Error downloading the image: {e}")
            return ""
    else:
        # Assume the content is already in base64
        base64_data = file_uri

    return base64_data
```

*Actions*: 
    - Create a new step to add the functionality of this snipped code into the file module.
    - Perform all adjustments on the snipped code to:
        . Add suitable checks to guarantee that the given file is in the base64 format before returning, adding the best treatment for the last else;
        . Add robust error treatments;
        . Add all necessary libraries;
        . Integrate it with the system logging;
        . Add the suitable docstrings and logging debug and info;
        . Add the suitable unit tests to the new functionality;
    - Update all related documentations:
        . README.md
        . TODO.md
        . SPEC.md
    - Update the memory bank
