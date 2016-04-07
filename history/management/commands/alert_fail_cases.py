import datetime
from django.conf import settings
from django.core.management.base import BaseCommand
from history.models import PredictionTest, TradeRecommendation, get_time


class Command(BaseCommand):

    help = 'sends email if a fail condition is met'

    def alert_email(self, fail_message):
        import smtplib
        sender = [settings.ALERT_EMAIL]
        receivers = [settings.ALERT_EMAIL]

        message = 'From: {0}\nTo: {0}\nSubject: Fail case\n\n{1}\n'.format(
            settings.ALERT_EMAIL,
            fail_message
        )

        try:
            smtpObj = smtplib.SMTP(settings.SMTP_HOST, 587)
            smtpObj.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            smtpObj.sendmail(sender, receivers, message)
            smtpObj.quit()
            print("Successfully sent email")
        except Exception as e:
            print("Error: unable to send email")
            print(e)

    def handle(self, *args, **options):
        last_pt = PredictionTest.objects.filter(type='mock').order_by('-created_on').first()
        last_trade = TradeRecommendation.objects.order_by('-created_on').first()

        print(last_pt.created_on)
        print(last_trade.created_on)

        # 7 hours thing is a hack for MST vs UTC timezone issues
        is_trader_running = last_trade.created_on > (
            get_time() - datetime.timedelta(hours=int(7)) - datetime.timedelta(minutes=int(15)))
        is_trainer_running = last_pt.created_on > (get_time() - datetime.timedelta(hours=int(7)) -
                                                   datetime.timedelta(minutes=int(15)))

        if not is_trader_running:
            self.alert_email("not is_trader_running")
        if not is_trainer_running:
            self.alert_email("not is_trainer_running")
