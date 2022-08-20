import re

import setuptools

from funing import *
from funing.settings import *

long_description = open("README.md", "r", encoding="utf-8").read()

_app_author = app_author
app_author = app_maintainer = _app_author[0]
app_author_email = app_maintainer_email = _app_author[1]
packages = setuptools.find_namespace_packages(exclude=["venv", "tests"])

setuptools.setup(
    name=app_name,
    version=app_version,
    author=app_author,
    author_email=app_author_email,
    description=app_description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=app_url,
    packages=packages,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            "funing=funing:run",
        ]
    },
    python_requires=">=3.6",
    install_requires=get_dep_requirements(),
    include_package_data=True,
)
