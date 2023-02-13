from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    is_driver = models.BooleanField(default=False)
    is_passenger = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        is_new = self.id is None
        super(User, self).save()
        if is_new:
            if self.is_passenger:
                PassengerUser.objects.create(user=self)
            elif self.is_driver:
                DriverUser.objects.create(user=self)


class PassengerUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    amount_of_money = models.FloatField(default=0)


class DriverUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    amount_of_money = models.FloatField(default=0)
    rating = models.FloatField(default=0)  # include this condition inside an if statement when calculating rating
    number_of_ratings = models.IntegerField(default=0)


# more information about potential values of "on_delete="
# https://stackoverflow.com/questions/38388423/what-does-on-delete-do-on-django-models

class OrderStatus(models.IntegerChoices):
    UNASSIGNED = 0, 'Unassigned'
    ASSIGNED = 1, 'Assigned'
    IN_PROGRESS = 2, 'In Progress'
    COMPLETED = 3, 'Completed'
    NEW_ORDER = 4, 'New'


class Order(models.Model):
    id = models.IntegerField(primary_key=True)
    start_location_lat = models.CharField(max_length=20)
    start_location_lon = models.CharField(max_length=20)
    destination_lat = models.CharField(max_length=20)
    destination_lon = models.CharField(max_length=20)
    start_name = models.CharField(max_length=100)
    destination_name = models.CharField(max_length=100)
    distance = models.FloatField(default=0)
    passenger = models.ForeignKey(PassengerUser, on_delete=models.SET_DEFAULT, default=None, null=True)
    driver = models.ForeignKey(DriverUser, on_delete=models.SET_DEFAULT, default=None, null=True)
    price = models.FloatField(default=0)
    is_rated = models.BooleanField(default=False)
    status = models.IntegerField(choices=OrderStatus.choices, default=OrderStatus.NEW_ORDER)

    def setStatusAndPayPercent(self, status: OrderStatus, percent: int):
        self.status = status
        need_to_pay = float("{:.2f}".format(self.price)) * float(percent) / 100.0
        self.driver.amount_of_money += need_to_pay
        self.passenger.amount_of_money -= need_to_pay
        self.driver.save()
        self.passenger.save()
        self.save()
