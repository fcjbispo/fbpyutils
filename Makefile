include .env

setup:
	pipenv --python 3.8
	pipenv update
	pipenv install --dev

freeze: Pipfile
	pipenv run pip freeze > requirements.txt

clean:
	find . -type d -name __pycache__ -print0 | xargs -0 rm -rf

coverage:
	pipenv run python -m pytest --cov-report xml

wheel:
	pipenv-setup sync
	pipenv run python setup.py bdist_wheel
	cp -fv dist/$(shell ls dist | sort -r | head -1) ${BUILD_DIST}/
