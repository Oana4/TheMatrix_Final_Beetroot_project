from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.db import transaction

from chat.models import Room
from .models import User


class NewDriverForm(UserCreationForm):
    email = forms.EmailField(max_length=150)

    class Meta(UserCreationForm.Meta):
        model = User

    @transaction.atomic
    def save(self):
        email = self.cleaned_data["email"]
        user = super().save(commit=False)
        user.email = email
        user.is_driver = True
        user.save()
        # Room.objects.create(name=f"Current Order", slug=f"{user.username}_chat_order", user1=None, user2=user)
        # when an order is created, user1 will be the passenger. I made rooms.html not show rooms with user1=None
        Room.objects.create(user1=user, user2=None)
        return user


class NewPassengerForm(UserCreationForm):
    email = forms.EmailField(max_length=150)

    class Meta(UserCreationForm.Meta):
        model = User

    @transaction.atomic
    def save(self):
        email = self.cleaned_data["email"]
        user = super().save(commit=False)
        user.email = email
        user.is_passenger = True
        user.save()
        Room.objects.create(user1=user, user2=None)
        return user


class NewOrderForm(forms.Form):
    start_location = forms.CharField(label='Start Location', max_length=50, widget=forms.TextInput(attrs={'onfocus': 'select_pin(this)'}))
    end_location = forms.CharField(label='Destination', max_length=50, widget=forms.TextInput(attrs={'onfocus': 'select_pin(this)'}))

    def startCoordinates(self) -> list:
        coordinate_string = self.data['start_location']
        return [float(s) for s in coordinate_string.strip()[1:-1].split(", ")]

    def stopCoordinates(self) -> list:
        coordinate_string = self.data['end_location']
        return [float(s) for s in coordinate_string.strip()[1:-1].split(", ")]


class AddMoneyForm(forms.Form):
    amount = forms.FloatField()
