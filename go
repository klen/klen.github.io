#!/bin/sh

RED='\033[1;31m'
GREEN='\033[0;32m'
CFG_REPO=https://github.com/klen/.home.git

command -v apt-get 1>/dev/null  || { 
    echo $RED"apt-get not found, exiting"
    exit 2
}

sudo apt-get update
sudo apt-get install ansible git -y

echo $GREEN"Bootstrap $(hostname -f)"
git clone --recursive --depth=10 $CFG_REPO $HOME/.home && {
    cd $HOME/.home
    ansible-playbook -i inventory setup/playbook.yml -c local -sK
    cd -
}
