import datetime

import praw

from django.core.management.base import BaseCommand
from django.conf import settings
from history.models import SocialNetworkMention


class Command(BaseCommand):

    help = 'pulls reddit mentions and stores them in a DB'

    def handle(self, *args, **options):

        r = praw.Reddit(user_agent='pytrader')
        limit = 20

        for subreddit_name, currencies in settings.SOCIAL_NETWORK_SENTIMENT_CONFIG['reddit'].items():
            print(subreddit_name)
            subreddit = r.get_subreddit(subreddit_name)
            submission_set = [
                subreddit.get_hot(limit=limit),
                subreddit.get_new(limit=limit),
                subreddit.get_rising(limit=limit),
            ]
            for submissions in submission_set:
                for x in submissions:
                    network_created_on = datetime.datetime.fromtimestamp(x.created_utc)
                    if SocialNetworkMention.objects.filter(network_name='reddit', network_id=x.id).count() == 0:
                        for currency_symbol in currencies:
                            snm = SocialNetworkMention.objects.create(
                                network_name='reddit',
                                network_id=x.id,
                                network_created_on=network_created_on,
                                network_username=str(x.author),
                                text=x.selftext,
                                symbol=currency_symbol,
                            )
                            snm.set_sentiment()
                            snm.save()

                            print('saving {}'.format(currency_symbol))
