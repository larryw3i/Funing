import re

import setuptools

from funing import *
from funing.settings import *

long_description = open("README.md", "r", encoding="utf-8").read()

appmaintainer = appauthor
appmaintainer_email = appauthor_email

setuptools.setup(
    name=app_name,
    version=app_version,
    author=app_author[0],
    author_email=app_author[1],
    description=app_description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=app_url,
    packages=setuptools.find_packages(),
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
