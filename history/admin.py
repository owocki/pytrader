from django.contrib import admin
from history.models import (
    Price, PredictionTest, Trade, TradeRecommendation, Balance, PerformanceComp,
    Deposit, ClassifierTest, SocialNetworkMention
)


class BalanceAdmin(admin.ModelAdmin):
    ordering = ['-id']
    search_fields = ['symbol']
    list_display = ['pk', 'created_on', 'symbol', 'coin_balance', 'btc_balance', 'usd_balance']

admin.site.register(Balance, BalanceAdmin)


class TradeAdmin(admin.ModelAdmin):
    ordering = ['-created_on']
    search_fields = ['type', 'symbol']
    list_display = ['pk', 'price', 'status', 'created_on_str', 'symbol', 'type', 'amount']
    readonly_fields = ['recommendation', 'algo']

    def recommendation(self, obj):
        trs = TradeRecommendation.objects.filter(trade=obj)
        return ",".join(["<a href='/admin/history/traderecommendation/{}'>Trade Rec {}</a>".
                         format(tr.pk, tr.pk) for tr in trs])

    recommendation.allow_tags = True

    def algo(self, obj):
        trs = TradeRecommendation.objects.filter(trade=obj)
        html = ""
        if trs.count:
            tr = trs[0]
            if tr.clf:
                html += "<a href='/admin/history/classifiertest/{}'>{}</a>".format(tr.clf.pk, tr.clf)
            if tr.made_by:
                html += "<a href='/admin/history/predictiontest/{}'>{}</a>".format(tr.made_by.pk, tr.made_by)
        return html

    algo.allow_tags = True

admin.site.register(Trade, TradeAdmin)


class PriceAdmin(admin.ModelAdmin):
    ordering = ['-id']
    search_fields = ['price', 'symbol']
    list_display = ['pk', 'price', 'created_on', 'symbol']


admin.site.register(Price, PriceAdmin)


class PredictionTestAdmin(admin.ModelAdmin):
    ordering = ['-id']
    search_fields = ['symbol', 'output']
    list_display = ['pk', 'type', 'symbol', 'created_on', 'percent_correct', 'profitloss', 'prediction_size']

admin.site.register(PredictionTest, PredictionTestAdmin)


class PerformanceCompAdmin(admin.ModelAdmin):
    ordering = ['-id']
    search_fields = ['symbol']
    list_display = ['pk', 'created_on', 'symbol', 'nn_rec', 'actual_movement', 'delta']

admin.site.register(PerformanceComp, PerformanceCompAdmin)


class TradeRecommendationAdmin(admin.ModelAdmin):
    ordering = ['-id']
    search_fields = ['symbol', 'recommendation']
    list_display = ['pk', 'created_on', 'symbol', 'recommendation', 'confidence']

admin.site.register(TradeRecommendation, TradeRecommendationAdmin)


class DepositAdmin(admin.ModelAdmin):
    ordering = ['-id']
    search_fields = ['symbol', 'amount', 'status']
    list_display = ['pk', 'symbol', 'amount', 'status']

admin.site.register(Deposit, DepositAdmin)


class ClassifierTestAdmin(admin.ModelAdmin):
    def view_link(obj):
        return u"<a href='{}'>View</a>".format(obj.graph_url())
    view_link.short_description = ''
    view_link.allow_tags = True

    ordering = ['-id']
    search_fields = ['symbol', 'output']
    list_display = ['pk', 'type', 'symbol', 'name', 'created_on',
                    'percent_correct', 'score', 'prediction_size', view_link]

admin.site.register(ClassifierTest, ClassifierTestAdmin)


class SocialNetworkMentionAdmin(admin.ModelAdmin):
    ordering = ['-id']
    search_fields = ['symbol', 'network_name', 'network_id']
    list_display = ['symbol', 'network_name', 'network_id']

admin.site.register(SocialNetworkMention, SocialNetworkMentionAdmin)
