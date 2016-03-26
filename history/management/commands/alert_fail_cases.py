from django.core.management.base import BaseCommand
import datetime
from history.models import PredictionTest, TradeRecommendation, get_time

class Command(BaseCommand):

    help = 'sends email if a fail condition is met'

    def alert_email(self,fail_message):
        import smtplib
        sender = 'ksowocki@gmail.com'
        receivers = ['ksowocki@gmail.com']

        message = """From: Kevin Owocki <ksowocki@gmail.com>
        To:  Kevin Owocki <ksowocki@gmail.com>
        Subject: Fail Case - """ + fail_message + """

        """ + fail_message + """
        """

        try:
           smtpObj = smtplib.SMTP('smtp.sendgrid.net',587)
           smtpObj.login('pytrader1','duw70s9pe9nG5BgiNUr')
           smtpObj.sendmail(sender, receivers, message)   
           smtpObj.quit()      
           print "Successfully sent email"
        except Exception as e:
           print "Error: unable to send email"
           print(e)


    def handle(self, *args, **options):
        last_pt = PredictionTest.objects.filter(type='mock').order_by('-created_on').first()
        last_trade = TradeRecommendation.objects.order_by('-created_on').first()

        print(last_pt.created_on)
        print(last_trade.created_on)

        # 7 hours thing is a hack for MST vs UTC timezone issues
        is_trader_running = last_trade.created_on > (get_time() - datetime.timedelta(hours=int(7)) - datetime.timedelta(minutes=int(15)))
        is_trainer_running = last_pt.created_on > (get_time() - datetime.timedelta(hours=int(7)) - datetime.timedelta(minutes=int(15)))

        if not is_trader_running:
            self.alert_email("not is_trader_running")
        if not is_trainer_running:
            self.alert_email("not is_trainer_running")

