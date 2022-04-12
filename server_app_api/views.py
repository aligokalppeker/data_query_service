import json
from datetime import datetime

from django.db.models import Avg, QuerySet, Max, Min, Q, Count
from django.db.models.functions import TruncMonth
from rest_framework import views, status
from rest_framework.response import Response

# Create your views here.
from .models import AveragePriceBusinessModel, HousePersistenceModel, HOUSE_TYPES
from .serializers import AveragePricesBusinessModelSerializer

MIN_PRICE_FIELD = "min_price"
MAX_PRICE_FIELD = "max_price"


class ViewCommon:
    @staticmethod
    def get_next_month(date: datetime) -> datetime:
        """
        Gets next month using the current month
        :param date: Date to increment month
        :return: Date with next month
        """
        return datetime(date.year + int(date.month / 12), ((date.month % 12) + 1), 1)

    @staticmethod
    def get_houses_filtered_by_date(start_date: datetime, end_date: datetime, postal_code: str) -> \
            QuerySet[HousePersistenceModel]:
        """
        Common filter method to be used for both average price and histogram capabilities.
        :param start_date: Start date
        :param end_date: End date
        :param postal_code: Postal code, empty string to select all
        :return: Query set for results
        """
        filtered_data: QuerySet[HousePersistenceModel] = HousePersistenceModel.objects.filter(sell_date__gte=start_date,
                                                                                              sell_date__lt=end_date)
        if postal_code:
            filtered_data = filtered_data.filter(postal_code__exact=postal_code)
        return filtered_data


class GetAveragePricesView(views.APIView):
    """
    Service for getting average prices for a given period.
    It takes start date, end date and postal code to fetch the data and calculate means.
    """

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
        filtered_data: QuerySet = ViewCommon.get_houses_filtered_by_date(start_date, end_date, postal_code)
        filtered_data: QuerySet = filtered_data.filter(house_type__exact=house_type)
        month_grouped_data: QuerySet = filtered_data.annotate(month_year_date=TruncMonth("sell_date")).values(
            "month_year_date")
        result: QuerySet = month_grouped_data.annotate(mean_sell_price=Avg("sell_price"))
        model_outputs: list[AveragePriceBusinessModel] = []
        for data in result:
            model_outputs.append(AveragePriceBusinessModel(**data))
        return AveragePricesBusinessModelSerializer(model_outputs, many=True).data

    def get(self, request, start_date: datetime, end_date: datetime, postal_code: str = "", *args, **kwargs):
        # Validate at start
        if end_date < start_date:
            return Response({"message": "End date should be later than start date."},
                            status=status.HTTP_400_BAD_REQUEST)

        result_response: dict[str, str] = {}
        # We lift the front end developers' job easier by querying data for each home types.
        # But we are compromising performance.
        # For better performance we can do it in one query and shift the segmentation job to the front-end side.
        for home_type_and_desc in HOUSE_TYPES:
            result_response[home_type_and_desc[1]] = self.get_data_for_house_type(start_date=start_date,
                                                                                  end_date=ViewCommon.get_next_month(
                                                                                      end_date),
                                                                                  house_type=home_type_and_desc[0],
                                                                                  postal_code=postal_code)

        return Response(result_response, status=status.HTTP_200_OK)


class NumberOfTransactionsView(views.APIView):
    """
    Service for getting transaction histogram for a given month/year point.
    It takes date as year-month, postal code and bin count to fetch the data and calculate the histogram.
    """

    def get(self, request, bin_count: int, date: datetime, postal_code: str = "", *args, **kwargs):
        # Validate at start
        if bin_count < 1:
            return Response({"message": "Bin count parameter should be at least 1."},
                            status=status.HTTP_400_BAD_REQUEST)

        # First query for getting the min and max prices
        filtered_data: QuerySet = ViewCommon.get_houses_filtered_by_date(start_date=date,
                                                                         end_date=ViewCommon.get_next_month(date),
                                                                         postal_code=postal_code)
        min_max_range: QuerySet = filtered_data.aggregate(max_price=Max("sell_price"), min_price=Min("sell_price"))
        max_price: int = min_max_range[MAX_PRICE_FIELD]
        min_price: int = min_max_range[MIN_PRICE_FIELD]
        response: Response = Response({"bins_range": "", "data": ""}, status=status.HTTP_200_OK)
        if min_price is not None and max_price is not None:
            # Keep bins and histogram params with same keys to preserve order
            histogram_aggregate_params: dict[str, Count] = {}
            bins: dict[str, tuple[int, int]] = dict()

            # Create query dynamically for getting the histogram
            step: float = (max_price - min_price) / bin_count
            for idx in range(0, bin_count):
                bin_price_start: float = min_price + (idx * step)
                bin_price_end: float = bin_price_start + step
                key_val_for_query: str = f"bin_{idx}"
                bins[key_val_for_query] = (int(bin_price_start), int(bin_price_end))
                histogram_aggregate_params[key_val_for_query] = Count("pk", filter=Q(
                    sell_price__gte=bin_price_start) and Q(sell_price__lte=bin_price_end))

            # Get the data
            histogram: dict[str, int] = filtered_data.aggregate(**histogram_aggregate_params)
            response = Response(
                {"bins_range": json.dumps(list(bins.values())), "data": json.dumps(list(histogram.values()))},
                status=status.HTTP_200_OK)

        return response
