#!/bin/bash

args=$*
app_name='funing'
apppy="${app_name}.py"
local_dir="${app_name}/locale"
pot_path="${local_dir}/${app_name}.pot"
mo0_path="${local_dir}/en_US/LC_MESSAGES/${app_name}.mo"
po0_path="${local_dir}/en_US/LC_MESSAGES/${app_name}.po"
cp_data_counter=0

py_version="$(python3 --version)"
[[ $py_version == *"3.11"* ]] && \
is_py311=1 || is_py311=0

[[ $py_version == *"3.10"* ]] && \
is_py310=1 || is_py310=0

[[ $py_version == *"3.9"* ]] && \
is_py39=1 || is_py39=0

echo_venv_dont_exist(){
    echo "Path both 'venv/bin' and 'venv/local/bin' don't exist."
}

echo_venv_used(){ 
    echo "virtualenv is used, enter 'deactivate' to exit."
}

if [[ -d "venv/local/bin" ]]
then
    bin_dir='venv/local/bin'
elif [[ -d "venv/bin" ]]
then 
    bin_dir='venv/bin' 
else
    echo_venv_dont_exist
fi

py3bin=${bin_dir}/python3

activate_venv(){
    # Use virtualenv 'venv' if exists
    if [[ -f "./venv/bin/activate" ]] 
    then
        . ./venv/bin/activate
        echo_venv_used
    elif [[ -f "./venv/local/bin/activate" ]]
    then
        . ./venv/local/bin/activate
        echo_venv_used
    else
        echo_venv_dont_exist
    fi

}

deactivate_venv(){
    deactivate
}

_args=("$@") # All parameters from terminal.

update_gitignore(){
    git rm -r --cached . && git add .
    read -p "commit now?(y/N)" commit_now
    [[ "Yy" == *"${commit_now}"* ]] && \
    git commit -m 'update .gitignore'
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

    for _po in $(find ${local_dir}/ -name "*.po")
    do
        msgmerge -U -v $_po ${pot_path}
    done
}

_msgfmt(){
    for _po in $(find ${local_dir} -name "*.po")
    do
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

cp_data(){
    cv2_source_dir=""
    cv2_source_data_dir=""
    cv2_source_LICENSE_path=""
    cv2_source_LICENSE_3RD_PARTY_path=""
    for v in {8..16}
    do
        cv2_source_dir0="${HOME}/.local/lib/python3.${v}/site-packages/cv2"
        cv2_source_data_dir0="${cv2_source_dir0}/data"
        if [[ -d ${cv2_source_data_dir0} ]]
        then
            cv2_source_dir=${cv2_source_dir0}
            cv2_source_data_dir=${cv2_source_data_dir0}
            cv2_source_LICENSE_path="${cv2_source_dir}/LICENSE.txt"
            rd3l="LICENSE-3RD-PARTY.txt"
            cv2_source_LICENSE_3RD_PARTY_path="${cv2_source_dir}/${rd3l}"
            break
        fi
    done
    
    if [[ "${cv2_source_data_dir}" == "" ]]
    then
        _pip3
        if [[ ${cp_data_counter} < 2 ]]
        then
            cp_data
            ((cp_data_counter++))
        fi
    else
        cv2_data_dir="${app_name}/data/cv2"
        cv2_facehaar_file_name="haarcascade_frontalface_default.xml"
        cv2_facehaar_path="${cv2_data_dir}/${cv2_facehaar_file_name}"
        cv2_LICENSE_path="${cv2_data_dir}/LICENSE.txt"
        cv2_LICENSE_3RD_PARTY_path="${cv2_data_dir}/LICENSE-3RD-PARTY.txt"

        [[ -d ${cv2_data_dir} ]] || mkdir -p ${cv2_data_dir}
        cp \
            ${cv2_source_LICENSE_path} \
            ${cv2_source_LICENSE_3RD_PARTY_path} \
            ${cv2_source_data_dir}/${cv2_facehaar_file_name} \
            ${cv2_data_dir}
    fi
}

bdist(){
    _msgfmt
    cp_data
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


pcd(){
    $py3bin ${app_name}.py pcd
}

prtf(){
    $py3bin ${app_name}.py prtf
}

test_funing(){
    ${bin_dir}/python3 ${app_name}.py test
}

print_help(){
    ${py3bin} ${app_name}.py h 
}
if [[ \
    $PATH != *"${PWD}/venv/local/bin"* && \
    $PATH != *"${PWD}/venv/bin"* ]]
then
    if [[ -d "${PWD}/venv" ]]
    then
        activate_venv
    elif [[ -x $(which virtualenv) ]]
    then 
        [[ $is_py311 == 1 ]] \
        && python3 -m venv venv \
        || virtualenv venv
        activate_venv
    else
        echo "virtualenv is not installed, cancel virtual environment."
    fi

fi

tu(){       twine_upload;       }
ugi(){      update_gitignore;   }
tst(){      test_funing;        }

gita(){     git_add;            }
bd(){       bdist;              }
kc(){       keep_code;          }

venv(){     activate_venv;      }
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
bk(){       blk;just_backup;    }
help(){     print_help;         }
# h(){        help;               }

if [[ $1 == "py" ]] 
then 
    ${py3bin} ${apppy} ${@:2}
elif [[ $# -eq 0 ]] || [[ "-h" == *"$*"* ]]
then
    if [[ "$0" != "-bash" ]];
    then
        cat $0
    fi
#     echo " 
#         tu(){       twine_upload;       }
#         ugi(){      update_gitignore;   }
#         tst(){      test_funing;        }
# 
#         gita(){     git_add;            }
#         bd(){       bdist;              }
#         kc(){       keep_code;          }
# 
#         venv(){     activate_venv;      }
#         msgf(){     _msgfmt;            }
#         xget(){     _xgettext;          }
# 
#         its(){       _i_test;           }
#         bdup(){     bd; tu;             }
#         s(){       _start;              }
# 
#         p3(){       venv;_pip3;         }
#         _cat(){     cat_bt;             }
#         _cat_(){    _cat | tr -s '\n';  }
# 
#         bdeb(){     bdist_deb;          }
#         wcl(){      _cat_ | wc -l;      }
#         blk(){      _black;             }
# 
#         4xget(){    gen4xget;           }
#         style(){    blk;                }
#         dep(){      p3;                 }
# 
#         depu(){     _pip3_u;            }
#         bk(){       just_backup;        }
#         help(){     print_help;         }
#    "  
else
    $*
fi


