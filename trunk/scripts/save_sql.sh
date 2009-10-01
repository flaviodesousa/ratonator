#! /bin/bash

dateref=`date +'%Y%m%d%H%M'`
source_path=~flavio/ratonator
sql_path=${source_path}/sql
new_sql=${sql_path}/front-${dateref}.sql
latest_sql=${sql_path}/front-latest.sql

${source_path}/manage.py sqlall front > ${new_sql}

diff ${new_sql} ${latest_sql} &&
    {
    echo No changes! Removing...
    rm ${new_sql}
    exit 1
    }

mv ${latest_sql} ${sql_path}/front-previous.sql
ln --symbolic --force ${new_sql} ${latest_sql}
