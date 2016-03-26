

IS_FAILURE=0
sudo su postgres -c "dropdb trader"
IS_FAILURE=$(expr $? + $IS_FAILURE )
sudo su postgres -c "psql -c 'create database trader;'"
IS_FAILURE=$(expr $? + $IS_FAILURE )
sudo su postgres -c "psql -c \"alter user trader with password '$PASSWORD';\""
IS_FAILURE=$(expr $? + $IS_FAILURE )
sudo su postgres -c "psql -c \"alter user trader superuser;\""
IS_FAILURE=$(expr $? + $IS_FAILURE )
sudo su postgres -c "psql -c 'grant all privileges on database trader to trader;'"
IS_FAILURE=$(expr $? + $IS_FAILURE )
