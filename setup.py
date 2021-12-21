
import os
import re

import pkg_resources
import setuptools

from funing import *

if 'opencv-python' in [i.key for i in pkg_resources.working_set]:
    print(
        "'opencv-python' and 'opencv-contrib-python' " +
        "are conflicting, Funing will uninstall 'opencv-python' " +
        "and install 'opencv-contrib-python'. . ."
    )
    os.system(
        'pip3 uninstall opencv-contrib-python opencv-python -v -y;' +
        'pip3 install opencv-contrib-python -v')


long_description = open("README.md", "r", encoding="utf-8").read()


def get_requirements():
    return [i.strip('\n') for i in
            open("./requirements/product.txt").readlines()]


setuptools.setup(
    name="funing",
    version=version,
    author=appauthor,
    author_email=appauthor_email,
    description="A face recognition gui",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/larryw3i/Funing",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
            'funing=funing:simple',
        ]
    },
    python_requires='>=3.6',
    install_requires=get_requirements(),
    include_package_data=True,
)
