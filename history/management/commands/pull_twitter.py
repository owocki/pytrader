import twitter

import datetime

from django.core.management.base import BaseCommand
from django.conf import settings
from history.models import SocialNetworkMention


class Command(BaseCommand):

    help = 'pulls twitter mentions and stores them in a DB'

    def handle(self, *args, **options):

        api = twitter.Api(consumer_key=settings.TWITTER_CONSUMER_KEY,
                          consumer_secret=settings.TWITTER_CONSUMER_SECRET,
                          access_token_key=settings.TWITTER_ACCESS_TOKEN_KEY,
                          access_token_secret=settings.TWITTER_ACCESS_TOKEN_SECRET)

        for currency_symbol in settings.SOCIAL_NETWORK_SENTIMENT_CONFIG['twitter']:
            print(currency_symbol)
            results = api.GetSearch("$" + currency_symbol, count=200)
            for tweet in results:

                if SocialNetworkMention.objects.filter(network_name='twitter', network_id=tweet.id).count() == 0:
                    snm = SocialNetworkMention.objects.create(
                        network_name='twitter',
                        network_id=tweet.id,
                        network_username=tweet.user.screen_name,
                        network_created_on=datetime.datetime.fromtimestamp(tweet.GetCreatedAtInSeconds()),
                        text=tweet.text,
                        symbol=currency_symbol,
                    )
                    snm.set_sentiment()
                    snm.save()
