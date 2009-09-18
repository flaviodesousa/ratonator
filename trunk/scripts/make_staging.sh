#! /bin/bash

dateref=`date +'%Y%m%d%H%M'`

cd ~flavio/projects

echo Creating source tree backup...
tar jcf /tmp/backup-ratonator-${dateref}.tar.bz2 ratonator

echo Copying source tree to staging...
cd ~flavio/staging
rm --recursive --force ratonator/*
cp --recursive ~flavio/projects/ratonator ~flavio/staging

echo Deleting sql scripts...
rm --recursive --force ratonator/sql

echo Deleting shell scripts...
rm --recursive --force ratonator/scripts

echo Deleting eric4 configurations...
rm --recursive --force ratonator/.eric4project

echo Deleting unwanted files...
find ratonator \( -name '*~' -o -name 'ratonator.e4p' -o -name '*po' \) -delete -print

echo Packaging deployment
tar jcf /tmp/deploy-ratonator-${dateref}.tar.bz2 ratonator

echo Sending to madelyn
scp /tmp/deploy-ratonator-${dateref}.tar.bz2 flavio@madelyn.moonlighting.com.br:~/staging

echo Aliasing to latest
ssh flavio@madelyn.moonlighting.com.br ln --force --symbolic ~/staging/deploy-ratonator-${dateref}.tar.bz2 ~/staging/deploy-ratonator-latest.tar.bz2
