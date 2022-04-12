"""server_app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from datetime import datetime

from django.contrib import admin
from django.urls import path, register_converter

from server_app_api.views import (
    GetAveragePricesView,
    NumberOfTransactionsView
)


class DateConverter:
    """
    Date converter class for the URL, it takes year and month as input separated with hypen,
    such as 2021-10, input is automatically converted to datetime type of variable
    """
    regex: str = "\\d{4}_\\d{2}"

    def to_python(self, value):
        return datetime.strptime(value, "%Y_%m")

    def to_url(self, value):
        return value


register_converter(DateConverter, "yyyy_mm")


class PostalCodeConverter:
    """
    Postal code converter, which takes a postal input with underscore "AAA_BBB" and converts it to "AAA BBB", by
    replacing underscore to space.
    """
    regex: str = "[a-zA-Z0-9_]+"

    def to_python(self, value):
        return value.replace("_", " ")

    def to_url(self, value):
        return value


register_converter(PostalCodeConverter, 'ppp_ppp')

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/avgprice/<yyyy_mm:start_date>/<yyyy_mm:end_date>", GetAveragePricesView.as_view()),
    path("api/avgprice/<yyyy_mm:start_date>/<yyyy_mm:end_date>/<ppp_ppp:postal_code>", GetAveragePricesView.as_view()),
    path("api/transaction/<int:bin_count>/<yyyy_mm:date>", NumberOfTransactionsView.as_view()),
    path("api/transaction/<int:bin_count>/<yyyy_mm:date>/<ppp_ppp:postal_code>", NumberOfTransactionsView.as_view()),
]
