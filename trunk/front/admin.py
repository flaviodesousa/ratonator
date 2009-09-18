from django.contrib import admin
from ratonator.front.models import *

admin.site.register(RateableUser)
admin.site.register(RateableStuff)
admin.site.register(NameableRateableStuff)
admin.site.register(ClassifiableRateableStuff)
