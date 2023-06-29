#!/bin/zsh

git add * 
git reset --soft master &&
git commit -m "foo" &&
git tag -d t &&
git tag t &&
PRODUCTION=0 ./build-docker.sh --skip-bitcoinonly --skip-core t
