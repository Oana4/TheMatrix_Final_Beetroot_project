from django.contrib import admin

from .models import PassengerUser, DriverUser, Order, User

admin.site.register(PassengerUser)
admin.site.register(DriverUser)
admin.site.register(User)
admin.site.register(Order)
