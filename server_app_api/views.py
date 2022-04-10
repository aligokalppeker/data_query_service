from datetime import datetime

from django.db.models import Avg, QuerySet
from django.db.models.functions import TruncMonth
from rest_framework import views, status
from rest_framework.response import Response

# Create your views here.
from .models import AveragePriceBusinessModel, HousePersistenceModel, HOUSE_TYPES
from .serializers import AveragePricesBusinessModelSerializer


class ViewCommon:
    @staticmethod
    def get_next_month(date):
        """
        Gets next month using the current month
        :param date: Date to increment month
        :return: Date with next month
        """
        return datetime(date.year + int(date.month / 12), ((date.month % 12) + 1), 1)

    @staticmethod
    def get_houses_filtered_by_date(start_date: datetime, end_date: datetime, postal_code: str) -> QuerySet:
        """
        Common filter method to be used for both average price and histogram capabilities.
        :param start_date: Start date
        :param end_date: End date
        :param postal_code: Postal code
        :return: Query set for results
        """
        filtered_data = HousePersistenceModel.objects.filter(sell_date__gte=start_date, sell_date__lte=end_date)
        if postal_code:
            filtered_data = filtered_data.filter(postal_code__exact=postal_code)
        return filtered_data


class GetAveragePricesView(views.APIView):

    @staticmethod
    def get_data_for_house_type(start_date: datetime, end_date: datetime, house_type: str,
                                postal_code: str = "") -> str:
        """
        Common method for filtering data using house type
        :param start_date: Start date
        :param end_date: End date
        :param house_type: House type
        :param postal_code: Postal code, empty string to select all
        :return: Filtered and serialized data
        """
        filtered_data = ViewCommon.get_houses_filtered_by_date(start_date, end_date, postal_code)
        filtered_data = filtered_data.filter(house_type__exact=house_type)
        month_grouped_data = filtered_data.annotate(month_year_date=TruncMonth("sell_date")).values("month_year_date")
        result = month_grouped_data.annotate(mean_sell_price=Avg("sell_price"))
        model_outputs = []
        for data in result:
            model_outputs.append(AveragePriceBusinessModel(**data))
        return AveragePricesBusinessModelSerializer(model_outputs, many=True).data

    def get(self, request, start_date: datetime, end_date: datetime, postal_code: str = "", *args, **kwargs):
        result_response: dict[str, str] = {}
        for home_type_and_desc in HOUSE_TYPES:
            result_response[home_type_and_desc[1]] = self.get_data_for_house_type(start_date=start_date,
                                                                                  end_date=ViewCommon.get_next_month(
                                                                                      end_date),
                                                                                  house_type=home_type_and_desc[0],
                                                                                  postal_code=postal_code)

        return Response(result_response, status=status.HTTP_200_OK)


class NumberOfTransactionsView(views.APIView):

    def get(self, request, date: datetime, postal_code: str = "", *args, **kwargs):
        filtered_data = ViewCommon.get_houses_filtered_by_date(start_date=date,
                                                               end_date=ViewCommon.get_next_month(date),
                                                               postal_code=postal_code)
        return Response({"data": "results"}, status=status.HTTP_200_OK)
