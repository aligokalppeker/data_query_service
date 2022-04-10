from django.contrib import admin

# Register your models here.
from server_app_api.models import HousePersistenceModel, AveragePriceBusinessModel

admin.site.register(HousePersistenceModel)
admin.site.register(AveragePriceBusinessModel)
