#!/bin/sh

RED='\033[1;31m'
GREEN='\033[0;32m'

[ -d $HOME/.home ] && {
    echo $RED"Already bootstraped." 
    exit 1
}


__command () {
    command -v $1 1>/dev/null
}


__command apt-get && {
    __command git || sudo apt-get install git -y
    __command make || sudo apt-get build-essential -y
}


echo $GREEN"Bootstrap $(hostname -f)"
git clone git://github.com/klen/.home.git $HOME/.home
cd $HOME/.home && make uninstall
cd $HOME/.home && make install
