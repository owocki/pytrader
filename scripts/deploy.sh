cd $HOME/pytrader
find . -name "*.pyc" -exec rm -rf {} \;
git pull origin master
crontab scripts/crontab.txt
cp -f scripts/bash_profile ../.bash_profile
./manage.py migrate
mkdir static
