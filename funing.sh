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

ug(){ update_gitignore; }

$1