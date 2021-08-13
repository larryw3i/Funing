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
    pip install -U setuptools wheel twine  launchpadlib
    pip install -r requirements.txt
    python3 test.py kc
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

tu(){   twine_upload; }
bd(){   bdist; }
ug(){   update_gitignore; }
gita(){ git_add;}

$1