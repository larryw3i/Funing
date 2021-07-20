#!/usr/bin/bash

git_push(){
    echo 'Push to git@gitee.com:larryw3i/Funing.git'
    git push git@gitee.com:larryw3i/Funing.git

    echo 'Push to git@github.com:larryw3i/Funing.git'
    git push git@github.com:larryw3i/Funing.git
}

update_gitignore(){
    git rm -r --cached .
    git add .
    read -p "commit now?(y/N)" commit_now
    if [ "$commit_now" = 'y' ] || [ "$commit_now" = 'Y' ]; then
        git commit -m 'update .gitignore'
    fi
    echo "gitignore updated!"
}

gp(){ git_push; }
ug(){ update_gitignore; }


$1