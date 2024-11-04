#!/bin/bash

if [[ -n $(git status -s) ]]
then
    git config --local user.email "whlit.cola@gmail.com"
    git config --local user.name "whlit"
    git add .
    git commit -m "auto update by $1"
    git push origin main
fi
