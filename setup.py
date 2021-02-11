import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="funing",
    version="0.2.02",
    author="larryw3i",
    author_email="larryw3i@163.com",
    description="A face recognition gui",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/larryw3i/Funing",
    packages=setuptools.find_packages(),
    scripts=['funing.py'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    data_files=[
        ('setting',['setting.yml.example', 'setting.py']),
        ('requirements',['requirements.txt']),
        ('snapcraft',['snapcraft.yaml']),
        ('readme',['README.md']),
        ('LICENSE',['LICENSE']),
        ('setup',['setup.py'])
    ],
    install_requires=[
        'dlib',
        'face-recognition',
        'opencv-python',
        'language_data',
        'langcodes',
        'pony',
        'pyyaml',
    ]
)