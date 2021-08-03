pip install -U setuptools wheel twine
pip install -r requirements.txt
python3 test.py kc
rm -rf dist/*
python setup.py sdist bdist_wheel
pip3 uninstall funing
pip3 install dist/*.whl