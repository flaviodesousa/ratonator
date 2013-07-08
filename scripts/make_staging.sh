#! /bin/bash

temp=/tmp
project_dir=ratonator
source_path=~flavio/dev/${project_dir}
staging_path=/tmp/staging
dateref=`date +'%Y%m%d%H%M'`
source_backup=/tmp/backup-ratonator-${dateref}.tar.bz2
deployment_archive=deploy-ratonator-${dateref}.tar.bz2
deployment_path=${temp}
shared_folder=/mnt/shared

[ -d ${staging_path} ] || mkdir ${staging_path} ||
{
    echo "No accessible staging path: ${staging_path}"
    exit 1
}

mountpoint -q ${shared_folder} ||
{
    echo "Shared folder not mounted...";
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
    "[ratonator-backup] backup for deploy ${dateref}" \
    "Project backup done in ${dateref}" \
    ${source_backup}

echo Copying backup to shared folder
cp ${source_backup} ${shared_folder}

echo Copying source tree to staging...
cd ${staging_path} &&
    rm --recursive --force ${staging_path}/${project_dir}/* &&
    cp --recursive ${source_path} ${staging_path} &&
    echo Deleting shell scripts... &&
    rm --recursive --force ${project_dir}/scripts

echo Deleting git bindings...
find ${staging_path} -name '.git' -exec rm -rf \{\} +

echo Deleting unwanted files...
find ${staging_path} \( -name '*~' -o -name '*po' -o -name '*.json' -o -name '*.sublime-*' \) -delete -print

echo Generating static/deploy.html
echo "<html><head><title>ratonator.com - deployment info</title></head><body><h1>Deploy ${dateref}</h1></body></html>" > ${staging_path}/${project_dir}/static/deploy.html

echo Copying templates and sending them to renato
cd ${staging_path}/${project_dir} &&
    zip -r -q ${shared_folder}/templates-${dateref} ratonator/templates/* front/static/* &&
    zip -r -q ${shared_folder}/static-${dateref} ratonator/static/* front/static/* &&
    ${source_path}/scripts/send_file.py \
        webrenat@gmail.com \
        "templates no deploy ${dateref}" \
        "Eis os templates constantes no deploy realizado em ${dateref}" \
        ${shared_folder}/templates-${dateref}* ${shared_folder}/static-${dateref}*

echo "Patching for production"
cd ${staging_path}/${project_dir}/ratonator
$source_path/scripts/mk.settings.pro.sh
sed -e 's/<!-- \(.*\)spaceless -->/{% \1spaceless %}/' < ${staging_path}/${project_dir}/templates/master.html > ${temp}/master.html-new &&
    mv -f ${temp}/master.html-new ${staging_path}/${project_dir}/templates/master.html
cd 
for h in ${staging_path}/${project_dir}/ratonator/templates/*html \
         ${staging_path}/${project_dir}/static/cacheable/__v_e_r_s_i_o_n__/css/*css ${staging_path}/${project_dir}/static/cacheable/__v_e_r_s_i_o_n__/js/thickbox/*js
do
    echo $h
    [ -f $h ] &&
        sed -e "s/__v_e_r_s_i_o_n__/${dateref}/g" < $h > ${h}-new &&
        mv -f ${h}-new $h
done
mv ${staging_path}/${project_dir}/front/static/cacheable/__v_e_r_s_i_o_n__ ${staging_path}/${project_dir}/front/static/cacheable/${dateref}

echo Packaging deployment
cd ${staging_path} && \
    tar jcf ${deployment_path}/${deployment_archive} ${project_dir}

echo Sending to madelyn
scp ${deployment_path}/${deployment_archive} flavio@madelyn.moonlighting.com.br:~/staging

echo Aliasing to latest
ssh flavio@madelyn.moonlighting.com.br ln --force --symbolic ~/staging/${deployment_archive} ~/staging/deploy-ratonator-latest.tar.bz2
