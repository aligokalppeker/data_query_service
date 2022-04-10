from django.db import models

TERRACE_HOME_TYPE = "T"
DETACHED_HOME_TYPE = "D"
SEMI_DETACHED_HOME_TYPE = "S"
FLATS_HOME_TYPE = "F"

HOUSE_TYPES = (
    (FLATS_HOME_TYPE, "flats"),
    (SEMI_DETACHED_HOME_TYPE, "semi-detached"),
    (DETACHED_HOME_TYPE, "detached"),
    (TERRACE_HOME_TYPE, "terraced")
)


class HousePersistenceModel(models.Model):
    house_uuid = models.CharField(max_length=40, default="")
    primary_addressable_object_name = models.CharField(max_length=50)
    secondary_addressable_object_name = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=10)
    sell_price = models.PositiveIntegerField()
    sell_date = models.DateTimeField()
    address_street = models.CharField(max_length=50)
    address_locality = models.CharField(max_length=50)
    address_town = models.CharField(max_length=50)
    address_county = models.CharField(max_length=50)
    address_city = models.CharField(max_length=50)

    house_type = models.CharField(max_length=1, choices=HOUSE_TYPES, default=FLATS_HOME_TYPE)


class AveragePriceBusinessModel(models.Model):
    mean_sell_price = models.PositiveIntegerField()
    month_year_date = models.DateTimeField()

    def save(self, *args, **kwargs):
        pass

    class Meta:
        managed = False
