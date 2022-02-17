#!/usr/bin/bash

_args=("$@") # All parameters from terminal.

update_gitignore(){
    git rm -r --cached . && git add .
    read -p "commit now?(y/N)" commit_now
    [[ "Yy" == *"${commit_now}"* ]] && git commit -m 'update .gitignore'
    echo "gitignore updated!"
}

_xgettext(){
    xgettext -v -j -L Python --output=funing/locale/funing.pot \
    $(find ./funing/ -name "*.py")
    xgettext -v -j -L glade --output=funing/locale/funing.pot \
    $(find ./funing/ui -name "*.ui")

    for _po in $(find ./funing/locale/ -name "*.po"); do
        msgmerge -U -v $_po ./funing/locale/funing.pot
    done
}

_msgfmt(){
    for _po in $(find ./funing/locale -name "*.po"); do
        echo -e "$_po ${_po/.po/.mo}"
        msgfmt -v -o ${_po/.po/.mo}  $_po
    done
}

p8(){
    isort ./funing/
    autopep8 -i -a -a -r -v ./funing/
    isort ./funing.py
    autopep8 -i -a -a -r -v ./funing.py
    isort ./setup.py
    autopep8 -i -a -a -r -v ./setup.py
    isort ./requirements/__init__.py
    autopep8 -i -a -a -r -v ./requirements/__init__.py
}

git_add(){
    p8; git add .
}

_pip3(){
    python3 funing.py p3
}

twine_upload(){
    twine upload dist/*
}

bdist(){
    _msgfmt
    rm -rf dist/ build/ funing.egg-info/
    python3 setup.py sdist bdist_wheel
}

bdist_deb(){
    rm -rf deb_dist/  dist/  funing.egg-info/ funing-0.2.48.tar.gz
    python3 setup.py --command-packages=stdeb.command bdist_deb
}

_i_test(){
    bdist
    pip3 uninstall funing -y
    pip3 install dist/*.whl
    funing
}

generate_po(){
    locale_path="./funing/locale"
    new_po_dir_path="${locale_path}/${_args[1]}/LC_MESSAGES"
    new_po_path="${new_po_dir_path}/funing.po"
    [[ -f ${new_po_path} ]] && echo "${new_po_path} exists." && return
    mkdir -p ${new_po_dir_path}
    cp ${locale_path}/funing.pot ${new_po_path}
}

keep_code(){
    _uuid=$(uuid)
    cp_dir_path="./.cp"
    uuid_dir_path="${cp_dir_path}/${_uuid//-/_}"
    [[ -d "${uuid_dir_path}" ]] || mkdir -p ${uuid_dir_path}
    mv build/ dist/ funing.build/ funing.egg-info/ ${uuid_dir_path}
}

_start(){
    [[ -f "./funing/locale/en_US/LC_MESSAGES/funing.mo" ]] || _msgfmt
    python3 funing.py t
}

active_venv(){
    [[ -f "./venv/bin/activate" ]] || \
    [[ -f $(which virtualenv) ]] && virtualenv venv || \
    echo "Installing virtualenv..." && pip3 install -U virtualenv
    source venv/bin/activate
}

cat_bt(){
    echo funing.sh; cat -bt funing.sh
    echo funing.py; cat -bt funing.py
    echo setup.py;  cat -bt setup.py
    for f in $(find ./funing/ -name "*.py" -o -name "*.ui")
    do
        echo $f
        cat -bt $f
    done
}

tu(){       twine_upload;       }
ugi(){      update_gitignore;   }
gpo(){      generate_po;        }

gita(){     git_add;            }
bd(){       bdist;              }
kc(){       keep_code;          }

p3(){       active_venv;_pip3;  }
msgf(){     _msgfmt;            }
xget(){     _xgettext;          }

its(){       _i_test;           }
bdup(){     bd; tu;             }
_s(){       _start;             }

venv(){     active_venv;        }
_cat(){     cat_bt;             }
_cat_(){    _cat | tr -s '\n';  }

bdeb(){     bdist_deb;          }

${_args[0]}
