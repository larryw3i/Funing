import setuptools
import re
with open("README.md", "r", encoding="utf-8") as fh:
    long_description=fh.read()

setting_yml_example = open('funing/setting.yml.example', 'r').read()
version = re.findall('[^_]version:\s*(\S+)\s*', setting_yml_example, re.S)[0]

setuptools.setup(
    name="funing",
    version=version,
    author="larryw3i",
    author_email="larryw3i@163.com",
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
        'dlib',
        'face-recognition',
        'opencv-python',
        'language_data',
        'langcodes',
        'pony',
        'pyyaml',
    ],
    include_package_data = True,
)
