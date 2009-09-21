#! /bin/bash

temp=/tmp
project_dir=ratonator
source_path=~flavio/${project_dir}
staging_path=~flavio/staging
dateref=`date +'%Y%m%d%H%M'`
source_backup=/tmp/backup-ratonator-${dateref}.tar.bz2
deployment_archive=deploy-ratonator-${dateref}.tar.bz2
deployment_path=${temp}
shared_folder=/mnt/shared


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

echo "Patching for production"
sed -e 's/DEBUG = True/DEBUG = False/' < ${staging_path}/${project_dir}/settings.py > ${temp}/settings.py-new &&
    mv -f ${temp}/settings.py-new ${staging_path}/${project_dir}/settings.py
sed -e 's/<!-- \(.*\)spaceless -->/{% \1spaceless %}/' < ${staging_path}/${project_dir}/templates/master.html > ${temp}/master.html-new &&
    mv -f ${temp}/master.html-new ${staging_path}/${project_dir}/templates/master.html

echo Packaging deployment
cd ${staging_path} && \
    tar jcf ${deployment_path}/${deployment_archive} ${project_dir}

echo Sending to madelyn
scp ${deployment_path}/${deployment_archive} flavio@madelyn.moonlighting.com.br:~/staging

echo Aliasing to latest
ssh flavio@madelyn.moonlighting.com.br ln --force --symbolic ~/staging/${deployment_archive} ~/staging/deploy-ratonator-latest.tar.bz2
