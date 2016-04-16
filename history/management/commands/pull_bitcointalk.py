import requests

import datetime

from django.core.management.base import BaseCommand
from django.conf import settings
from history.models import SocialNetworkMention

import xml.etree.ElementTree as ET
from BeautifulSoup import BeautifulSoup


def monthToNum(date):

    return{
        'Jan': 1,
        'Feb': 2,
        'Mar': 3,
        'Apr': 4,
        'May': 5,
        'Jun': 6,
        'Jul': 7,
        'Aug': 8,
        'Sep': 9,
        'Oct': 10,
        'Nov': 11,
        'Dec': 12
    }[date]


def get_message_id(link):
    tmp = link.split('#msg')
    tmp.reverse()
    return tmp[0]


class Command(BaseCommand):

    help = 'pulls bitcointalk mentions and stores them in a DB'

    def handle(self, *args, **options):

        rss_url = 'https://bitcointalk.org/index.php?type=rss;action=.xml'
        response = requests.get(rss_url)
        root = ET.fromstring(response.text.encode('utf-8'))
        for item in root.iter('item'):
            children = {child.tag: child.text.encode('utf-8') for child in item}
            post_link = children['link']
            response = requests.get(post_link)
            response_body = response.text.encode('utf-8')
            parsed_html = BeautifulSoup(response_body)
            post_body = parsed_html.find('div', attrs={'class': 'post'}).text
            message_id = get_message_id(children['guid'])
            tmp_date = children['pubDate'].split(' ')  # Sat, 16 Apr 2016 18:23:51 GMT
            tmp_time = tmp_date[4].split(':')  # 18:23:51
            network_created_on = datetime.datetime(int(tmp_date[3]), int(monthToNum(tmp_date[2])), int(tmp_date[1]), int(tmp_time[0]), int(tmp_time[1]), int(tmp_time[2]))
            if SocialNetworkMention.objects.filter(network_name='bitcointalk', network_id=message_id).count() == 0:
                for currency_symbol in settings.SOCIAL_NETWORK_SENTIMENT_CONFIG['bitcointalk']:
                    if currency_symbol.lower() in post_body.lower():
                        SocialNetworkMention.objects.create(
                            network_name='bitcointalk',
                            network_id=message_id,
                            network_created_on=network_created_on,
                            text=post_body,
                            symbol=currency_symbol,
                        )

                        print('saving {}'.format(currency_symbol))
