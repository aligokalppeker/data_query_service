from rest_framework import serializers

from .models import AveragePriceBusinessModel


class AveragePricesBusinessModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = AveragePriceBusinessModel
        fields = ["month_year_date", "mean_sell_price"]
