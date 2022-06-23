from funing import product_req

dev_req = [
    # ('package','version','project_url','license','license_url')
    (
        "pip",
        "",
        "https://github.com/pypa/pip",
        "MIT License",
        "https://github.com/pypa/pip/blob/main/LICENSE.txt",
    ),
    (
        "Babel",
        "",
        "https://github.com/python-babel/babel",
        "BSD License",
        "https://github.com/python-babel/babel/blob/master/LICENSE",
    ),
    (
        "autopep8",
        "",
        "https://github.com/hhatto/autopep8",
        "MIT License",
        "https://github.com/hhatto/autopep8/blob/master/LICENSE",
    ),
    (
        "isort",
        "",
        "https://github.com/pycqa/isort",
        "MIT License",
        "https://github.com/PyCQA/isort/blob/main/LICENSE",
    ),
    (
        "twine",
        "",
        "https://github.com/pypa/twine/",
        "Apache License 2.0",
        "https://github.com/pypa/twine/blob/main/LICENSE",
    ),
    (
        "pygubu-designer",
        "",
        "https://github.com/alejandroautalan/pygubu-designer",
        "GNU General Public License v3.0",
        "https://github.com/alejandroautalan/pygubu-designer/blob/"
        + "master/LICENSE.md",
    ),
] + product_req


def get_dev_req_str():
    return " ".join([r[0] + r[1] for r in dev_req])


def install_dev_req():
    os.system("pip3 install -U " + get_dev_req_str())
