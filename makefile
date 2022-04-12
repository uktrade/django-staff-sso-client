build: test_requirements pytest

clean:
	-find . -type f -name "*.pyc" -delete
	-find . -type d -name "__pycache__" -delete

test_requirements:
	pip install -e .[test]

flake8:
	flake8 . --exclude=.venv

pytest:
	pytest . -v --ignore=venv --cov=. $(pytest_args)

publish:
	rm -rf build dist; \
	python -m build; \
	twine upload --username $$PYPI_USERNAME --password $$PYPI_PASSWORD dist/*

.PHONY: build clean test_requirements flake8 pytest publish
