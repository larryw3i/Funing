import setuptools
import re
from funing.settings import version

long_description = open("README.md", "r", encoding="utf-8").read()
setuptools.setup(
    name="funing",
    version=version,
    author="larryw3i",
    author_email="",
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
            'funing=funing:run',
        ]
    },
    python_requires='>=3.6',
    install_requires=[
        'opencv-contrib-python >= 4.5.3.56',
        'PyYAML >= 5.3.1',
        'Pillow >= 8.3.0',
        'numpy >= 1.21.1',
    ],
    include_package_data = True,
)
