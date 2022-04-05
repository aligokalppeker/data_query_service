from django.db import models


class HouseItem(models.Model):
    house_uuid = models.CharField(max_length=200, default="")
    primary_addressable_object_name = models.CharField(max_length=200)
    secondary_addressable_object_name = models.CharField(max_length=200)
    sell_price = models.PositiveIntegerField()
    sell_date = models.DateTimeField()
    address_street = models.CharField(max_length=50)
    address_locality = models.CharField(max_length=50)
    address_town = models.CharField(max_length=50)
    address_county = models.CharField(max_length=50)
    address_city = models.CharField(max_length=50)
    HOUSE_TYPES = (
        ('F', 'Flats'),
        ('S', 'Semi-detached homes'),
        ('D', 'Detached homes'),
        ('T', 'Terraced homes')
    )
    house_type = models.CharField(max_length=1, choices=HOUSE_TYPES, default="F")
