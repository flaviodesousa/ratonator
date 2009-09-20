#! /bin/bash

project_dir=ratonator
source_path=~flavio/${project_dir}
staging_path=~flavio/staging
dateref=`date +'%Y%m%d%H%M'`
source_backup=/tmp/backup-ratonator-${dateref}.tar.bz2
deployment_archive=deploy-ratonator-${dateref}.tar.bz2
deployment_path=/tmp
shared_folder=/mnt/shared
remote_target_address=

cd ${source_path}

echo Creating source tree backups...
tar jcvf ${source_backup} ../${project_dir}
mountpoint -q ${shared_folder} && cp ${source_backup} ${shared_folder}

echo Copying source tree to staging...
cd ${staging_path}
rm --recursive --force ${project_dir}/*
cp --recursive ${source_path} ${staging_path}

echo Deleting sql scripts...
rm --recursive --force ${project_dir}/sql

echo Deleting shell scripts...
rm --recursive --force ${project_dir}/scripts

echo Deleting eric4 configurations...
rm --recursive --force ${project_dir}/.eric4project

echo Deleting subversion bindings...
find ${staging_path} -name '.svn' -exec rm -rf \{\} +

echo Deleting unwanted files...
find ${staging_path} \( -name '*~' -o -name 'ratonator.e4p' -o -name '*po' -o -name '*.json' \) -delete -print

echo Packaging deployment
tar jcf ${deployment_path}/${deployment_archive} ratonator

echo Sending to madelyn
scp ${deployment_path}/${deployment_archive} flavio@madelyn.moonlighting.com.br:~/staging

echo Aliasing to latest
ssh flavio@madelyn.moonlighting.com.br ln --force --symbolic ~/staging/${deployment_archive} ~/staging/deploy-ratonator-latest.tar.bz2
