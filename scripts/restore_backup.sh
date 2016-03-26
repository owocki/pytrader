scp root@trader.owocki.com:/tmp/backup.psql backup.psql

IS_FAILURE=0
dropdb trader
IS_FAILURE=$(expr $? + $IS_FAILURE )
psql -c 'create database trader;'
IS_FAILURE=$(expr $? + $IS_FAILURE )
psql -c "alter user trader with password '$PASSWORD';"
IS_FAILURE=$(expr $? + $IS_FAILURE )
psql -c "alter user trader superuser;"
IS_FAILURE=$(expr $? + $IS_FAILURE )
psql -c 'grant all privileges on database trader to trader;'
IS_FAILURE=$(expr $? + $IS_FAILURE )

if [ "$IS_FAILURE" -gt "0" ]; then
    echo "IMPORTANT: There was some issue with dropping db.  See above output ^^ and then try again."
    exit 1
else 
    pg_restore -Fc -d trader --no-owner 'backup.psql'
    cat backup.psql | psql trader

    rm -f backup.psql

fi

