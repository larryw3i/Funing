#!/usr/bin/bash

update_gitignore(){
    git rm -r --cached .
    git add .
    read -p "commit now?(y/N)" commit_now
    if [ "$commit_now" = 'y' ] || [ "$commit_now" = 'Y' ]; then
        git commit -m 'update .gitignore'
    fi
    echo "gitignore updated!"
}

twine_upload(){
    twine upload dist/*
}

bdist(){
    # pip install -U setuptools wheel twine  launchpadlib
    # pip install -r requirements.txt
    python3 test.py kc
    python3 funing.py pbc
    rm -rf dist/ build/ funing.egg-info/
    python3 setup.py sdist bdist_wheel
    pip3 uninstall funing
    pip3 install dist/*.whl
}

git_add(){
    isort ./funing/
    autopep8 -i -a -a -r  ./funing/
    isort ./funing.py
    autopep8 -i -a -a -r  ./funing.py
    git add .
}

locale_cn(){
    python3 funing.py bc
    cp -r funing/locale/zh_Hans/* funing/locale/zh_CN/
}

be_bu_bc(){
    python3 funing.py be bu bc
}

_pip3(){
    pip3 install -U -r requirements.txt
}

euc(){  be_bu_bc;}
tu(){   twine_upload; }
bd(){   lc; bdist; }
ug(){   update_gitignore; }
gita(){ git_add;}
lc(){   locale_cn;}
p3(){   _pip3;}

$1