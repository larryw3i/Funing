#!/usr/bin/bash

_args=("$@") # All parameters from terminal.

update_gitignore(){
    git rm -r --cached .
    git add .
    read -p "commit now?(y/N)" commit_now
    if [ "$commit_now" = 'y' ] || [ "$commit_now" = 'Y' ]; then
        git commit -m 'update .gitignore'
    fi
    echo "gitignore updated!"
}

_xgettext(){
    xgettext -v -j -L Python --output=funing/locale/funing.pot \
    `find ./funing/ -name "*.py"`

    for _po in $(find ./funing/locale/ -name "*.po"); do
        msgmerge -U -v $_po ./funing/locale/funing.pot
    done
}

_msgfmt(){
    for _po in $(find ./funing/locale -name "*.po"); do
        echo $_po ${_po/.po/.mo}
        msgfmt -v -o ${_po/.po/.mo}  $_po
    done
}

p8(){
    isort ./funing/
    autopep8 -i -a -a -r -v ./funing/
    isort ./funing.py
    autopep8 -i -a -a -r -v ./funing.py
}

git_add(){
    p8
    git add .
}

_pip3(){
    pip3 install -U -r requirements.txt
}

twine_upload(){
    twine upload --verbose dist/*
}

bdist(){
    _msgfmt
    rm -rf dist/ build/ funing.egg-info/
    python3 setup.py sdist bdist_wheel
}

_test(){
    bdist
    pip3 uninstall funing -y
    pip3 install dist/*.whl
    funing
}


tu(){       twine_upload;       }
ugi(){      update_gitignore;   }

gita(){     git_add;       }
bd(){       bdist;         }

p3(){       _pip3;              }
msgf(){     _msgfmt;            }
xget(){     _xgettext;          }

ts(){       _test;              }
bdup(){     bd; tu;             }

${_args[0]}
