screen -S predictNN bash -c 'while true; do cd pytrader; ./manage.py predict_many_v2; done'
screen -S predictSK bash -c 'while true; do cd pytrader; ./manage.py predict_many_sk; done'
screen -S trade bash -c 'while true; do cd pytrader; ./manage.py trade; done'
screen -S runserver bash -c 'while true; do cd pytrader; ./manage.py runserver 45.55.42.224:80; done'