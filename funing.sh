#!/usr/bin/bash

git_push(){
    echo 'Push to git@gitee.com:larryw3i/Funing.git'
    git push git@gitee.com:larryw3i/Funing.git

    echo 'Push to git@github.com:larryw3i/Funing.git'
    git push git@github.com:larryw3i/Funing.git
}

$1