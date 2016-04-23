import requests

import datetime

from django.core.management.base import BaseCommand
from django.conf import settings
from history.models import SocialNetworkMention

import xml.etree.ElementTree as ET
from BeautifulSoup import BeautifulSoup


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
            # Sat, 16 Apr 2016 18:23:51 GMT
            network_created_on = datetime.datetime.strptime(children['pubDate'],
                                                            "%a, %d %b %Y %X %Z")
            if SocialNetworkMention.objects.filter(network_name='bitcointalk', network_id=message_id).count() == 0:
                for currency_symbol in settings.SOCIAL_NETWORK_SENTIMENT_CONFIG['bitcointalk']:
                    if currency_symbol.lower() in post_body.lower():
                        snm = SocialNetworkMention.objects.create(
                            network_name='bitcointalk',
                            network_id=message_id,
                            network_created_on=network_created_on,
                            text=post_body,
                            symbol=currency_symbol,
                        )

                        snm.set_sentiment()
                        snm.save()

                        print('saving {}'.format(currency_symbol))
