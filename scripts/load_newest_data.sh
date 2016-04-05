#!/bin/sh

cd /root/pytrader
wget http://dumps.snipanet.com/history_price-latest.psql.gz
gunzip history_price-latest.psql.gz
export PGPASSWORD=$POSTGRES_PASSWORD
psql -h db -U trader trader < history_price-latest.psql
rm -f history_price-latest.psql
