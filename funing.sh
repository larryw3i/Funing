#!/bin/bash

args=$*
app_name='funing'
[[ -d "venv/local" ]] && bin_dir='venv/local/bin' || bin_dir='venv/bin'
local_dir="${app_name}/locale"
pot_path="${local_dir}/${app_name}.pot"
mo0_path="${local_dir}/en_US/LC_MESSAGES/${app_name}.mo"
po0_path="${local_dir}/en_US/LC_MESSAGES/${app_name}.po"

activate_venv(){
    # Use virtualenv 'venv' if exists
    echo "virtualenv is used, enter 'deactivate' to exit."
    for v in \
        "./venv/bin/activate" \
        "./venv/local/bin/activate" # python 3.10
    do
        [[ -f $v ]] && . $v
    done
}

deactivate(){
    deactivate
}

_args=("$@") # All parameters from terminal.

update_gitignore(){
    git rm -r --cached . && git add .
    read -p "commit now?(y/N)" commit_now
    [[ "Yy" == *"${commit_now}"* ]] && git commit -m 'update .gitignore'
    echo "gitignore updated!"
}

just_backup(){
    git add . && \
    git commit -m "$(date -R -u) backup." && \
    git push
}

_xgettext(){
    [[ -f $pot_path ]] || touch $pot_path

    xgettext -v -j -L Python --output=${pot_path} \
    $(find ${app_name} -name "*.py")

    [[ -f $po0_path ]] || touch $po0_path

    for _po in $(find ${local_dir}/ -name "*.po"); do
        msgmerge -U -v $_po ${pot_path}
    done
}

_msgfmt(){
    for _po in $(find ${local_dir} -name "*.po"); do
        echo -e "$_po --> ${_po/.po/.mo}"
        msgfmt -v -o ${_po/.po/.mo} $_po
    done
}

p8(){
    isort ${app_name}/
    autopep8 -i -a -a -r -v ${app_name}/
    isort ${app_name}.py
    autopep8 -i -a -a -r -v ${app_name}.py
    isort ./setup.py
    autopep8 -i -a -a -r -v ./setup.py
}

_black(){
    isort ${app_name}/
    isort ${app_name}.py
    isort setup.py
    python3 -m black -l 79 ${app_name}/;
    python3 -m black -l 79 ${app_name}.py;
    python3 -m black -l 79 setup.py;
}

git_add(){
    _black;
    git add .;
}

_pip3(){
    ${bin_dir}/python3 ${app_name}.py dep
}

_pip3_u(){
    ${bin_dir}/python3 ${app_name}.py depu
}

twine_upload(){
    twine upload dist/*
}

bdist(){
    _msgfmt
    rm -rf dist/ build/ ${app_name}.egg-info/
    ${bin_dir}/python3 setup.py sdist bdist_wheel
}

bdist_deb(){
    rm -rf deb_dist/  dist/  ${app_name}.egg-info/ ${app_name}*.tar.gz
    ${bin_dir}/python3 setup.py --command-packages=stdeb.command bdist_deb
}

_i_test(){
    bdist
    ${bin_dir}/pip3 uninstall ${app_name} -y
    ${bin_dir}/pip3 install dist/*.whl
    ${app_name}
}

_start(){
    _black
    [[ -f "${mo0_path}" ]] || _msgfmt
    ${bin_dir}/python3 ${app_name}.py $args
}

gen4xget(){
    ${bin_dir}/python3 ${app_name}.py 4xget
}

cat_bt(){
    echo ${app_name}.sh; cat -bt ${app_name}.sh
    echo ${app_name}.py; cat -bt ${app_name}.py
    echo setup.py;  cat -bt setup.py
    for f in $(\
        find ${app_name}/ \
        -type f \
        -name "*.py" \
        -o -name "*.po" \
        -o -name "*.pot")
    do
        [[ -f $f ]] || continue
        echo $f
        cat -bt $f
    done
}

test(){
    ${bin_dir}/python3 ${app_name}.py test
}

if [[ \
    $PATH != *"${PWD}/venv/local/bin"* && \
    $PATH != *"${PWD}/venv/bin"* ]]
then
    if [[ -d "${PWD}/venv" ]];then
        activate_venv
    elif [[ -x $(which virtualenv) ]]
    then 
        virtualenv venv
        activate_venv
    else
        echo "virtualenv is not installed, cancel virtual environment."
    fi

fi

tu(){       twine_upload;       }
ugi(){      update_gitignore;   }
tst(){      test;               }

gita(){     git_add;            }
bd(){       bdist;              }
kc(){       keep_code;          }

venv(){     activate_venv;        }
msgf(){     _msgfmt;            }
xget(){     _xgettext;          }

its(){       _i_test;           }
bdup(){     bd; tu;             }
s(){       _start;              }

p3(){       venv;_pip3;         }
_cat(){     cat_bt;             }
_cat_(){    _cat | tr -s '\n';  }

bdeb(){     bdist_deb;          }
wcl(){      _cat_ | wc -l;      }
blk(){      _black;             }

4xget(){    gen4xget;           }
style(){    blk;                }
dep(){      p3;                 }

depu(){     _pip3_u;            }
bk(){       just_backup;        }

$*

