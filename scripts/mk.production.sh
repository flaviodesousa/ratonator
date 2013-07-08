#! /bin/sh

dateref=`date +'%Y%m%d%H%M'`
source_backup=/tmp/backup-ratonator-${dateref}.tar.bz2
deployment_archive=deploy-ratonator-${dateref}.tar.bz2
deploy_base=/var/www/rate228/app/
staging_dir=${deploy_base}/_ratonator.next/
backup_dir=${deploy_base}/_ratonator.previous/
deployment_path=${temp}

cd ${deploy_base}

echo Backing up production

echo Generating static/deploy.html
echo "<html><head><title>ratonator.com - deployment info</title></head><body><h1>Deploy ${dateref}</h1></body></html>" > ${staging_path}/static/deploy.html

echo "Patching for production"

sed -e 's/<!-- \(.*\)spaceless -->/{% \1spaceless %}/' < ${staging_path}/${project_dir}/templates/master.html > ${temp}/master.html-new &&
    mv -f ${temp}/master.html-new ${staging_path}/${project_dir}/templates/master.html
for h in ${staging_path}/${project_dir}/templates/*html ${staging_path}/${project_dir}/static/cacheable/__v_e_r_s_i_o_n__/css/*css ${staging_path}/${project_dir}/static/cacheable/__v_e_r_s_i_o_n__/js/thickbox/*js
do
    echo $h
    [ -f $h ] &&
        sed -e "s/__v_e_r_s_i_o_n__/${dateref}/g" < $h > ${h}-new &&
        mv -f ${h}-new $h
done
mv \
	${staging_path}/${project_dir}/static/cacheable/__v_e_r_s_i_o_n__ \
	${staging_path}/${project_dir}/static/cacheable/${dateref}
