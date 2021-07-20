pip install -U setuptools
pip install -U wheel
pip install -U twine
python3 test.py kc
rm -rf dist/*
python setup.py sdist bdist_wheel
pip3 uninstall funing
pip install dist/*.whl

