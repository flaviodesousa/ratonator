#! /bin/bash

temp=/tmp
project_dir=ratonator
source_path=~flavio/dev/${project_dir}
staging_path=/tmp/staging
dateref=`date +'%Y%m%d%H%M'`
source_backup=/tmp/backup-ratonator-${dateref}.tar.xz
deployment_archive=deploy-ratonator-${dateref}.tar.xz
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

cd ${source_path}/..

echo Creating source tree backups...
tar Jcf ${source_backup} ${project_dir} ||
{
    echo error creating backup;
    exit 1;
}

cd ${source_path}

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
rm --recursive --force ${staging_path}/${project_dir}/.git

echo Deleting unwanted files...
find ${staging_path} \( -name '*~' -o -name '*pyc' -o -name '*po' -o -name '*.sublime-*' \) -delete

echo Generating static/deploy.html
echo "<html><head><title>ratonator.com - deployment info</title></head><body><h1>Deploy ${dateref}</h1></body></html>" > ${staging_path}/${project_dir}/front/static/deploy.html

echo "Patching for production"
cd ${staging_path}/${project_dir}/ratonator
$source_path/scripts/mk.settings.pro.sh
sed -e 's/<!-- \(.*\)spaceless -->/{% \1spaceless %}/' \
        < ${staging_path}/${project_dir}/ratonator/templates/master.html \
        > ${temp}/master.html-new &&
    mv -f \
        ${temp}/master.html-new \
        ${staging_path}/${project_dir}/ratonator/templates/master.html

echo "Setting cacheable directory"
for h in ${staging_path}/${project_dir}/ratonator/templates/*html \
         ${staging_path}/${project_dir}/front/static/cacheable/__v_e_r_s_i_o_n__/css/*css \
         ${staging_path}/${project_dir}/front/static/cacheable/__v_e_r_s_i_o_n__/js/thickbox/*js
do
    sed -e "s/__v_e_r_s_i_o_n__/${dateref}/g" < $h > ${h}-new &&
        mv -f ${h}-new $h
done
mv ${staging_path}/${project_dir}/front/static/cacheable/__v_e_r_s_i_o_n__ ${staging_path}/${project_dir}/front/static/cacheable/${dateref}

echo Packaging deployment
cd ${staging_path} &&
    tar Jcf ${deployment_path}/${deployment_archive} ${project_dir}

echo Sending to production server
scp ${deployment_path}/${deployment_archive} flavio@david.flaviodesousa.com:~/staging

echo Aliasing to latest
ssh flavio@david.flaviodesousa.com ln --force --symbolic ~/staging/${deployment_archive} ~/staging/deploy-ratonator-latest.tar.xz
