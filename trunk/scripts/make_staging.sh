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

mountpoint -q ${shared_folder} ||
{
    echo "Falta montar o shared folder...";
    exit 1;
}

cd ${source_path}

echo Creating source tree backups...
tar jcvf ${source_backup} ../${project_dir} ||
{
    echo error creating backup;
    exit 1;
}

echo Sending backup to flavio@moonlighting.com.br
${source_path}/scripts/send_file.py \
    flavio@moonlighting.com.br \
    "[ratonator-backup] backup no deploy ${dateref}" \
    "Project backup done in ${dateref}" \
    ${source_backup}

echo Copying backup to shared folder
cp ${source_backup} ${shared_folder}

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

echo Generating static/deploy.html
echo "<html><head><title>ratonator.com - deployment info</title></head><body><h1>Deploy ${dateref}</h1></body></html>" > ${staging_path}/${project_dir}/static/deploy.html

echo Copying templates and sending them to renato
cd ${staging_path}/${project_dir} &&
    zip -r -q ${shared_folder}/templates-${dateref} templates/* &&
    zip -r -q ${shared_folder}/static-${dateref} static/* &&
    ${source_path}/scripts/send_file.py \
        webrenat@gmail.com \
        "templates no deploy ${dateref}" \
        "Eis os templates constantes no deploy realizado em ${dateref}" \
        ${shared_folder}/templates-${dateref}* ${shared_folder}/static-${dateref}*

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
