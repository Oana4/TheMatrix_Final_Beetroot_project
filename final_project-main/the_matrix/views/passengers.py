from django.contrib.auth import login
from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.generic import CreateView
from django.conf import settings
from django.db.models import Q
from django.http import HttpResponseRedirect
from geopy import GoogleV3
import googlemaps

from ..forms import NewPassengerForm, NewOrderForm, AddMoneyForm
from ..models import User, PassengerUser, Order, OrderStatus
from ..decorators import passenger_required
from chat.models import Room
from main_app.settings import GOOGLE_API_KEY


class PassengerSignUpView(CreateView):
    model = User
    form_class = NewPassengerForm
    template_name = 'main_app/register_passenger.html'  # to be changed after we make a separate register

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'passenger'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('passenger_page')


@passenger_required
def passenger_page(request):
    usr: User = request.user
    passenger = PassengerUser.objects.get(user=usr)
    passenger_orders = Order.objects.filter(passenger=passenger).all()
    last_order = passenger_orders.last()
    return render(request, 'main_app/passenger_page.html', context={'order': last_order})


@passenger_required
def passenger_new_order(request):
    print(request.POST)
    usr: User = request.user
    passenger = PassengerUser.objects.get(user=usr)
    available_orders = Order.objects.filter(passenger=passenger).filter(
        ~Q(status=OrderStatus.COMPLETED))  # ~ == NOT. Here we return only active orders for passenger
    last_order = available_orders.last()
    if last_order is None:
        last_order = Order(passenger=passenger, status=OrderStatus.NEW_ORDER, price=6.0)
        last_order.save()
    if last_order.status == OrderStatus.NEW_ORDER:
        start_init = f"({last_order.start_location_lat}, {last_order.start_location_lon})" if (last_order.start_location_lat and last_order.start_location_lon) else ""
        end_init = f"({last_order.destination_lat}, {last_order.destination_lon})" if (last_order.destination_lat and last_order.destination_lon) else ""
        data = {
            'start_location': start_init,
            'end_location': end_init}
        form = NewOrderForm(initial=data)
        context = {
            'order': last_order,
            'order_status_label': OrderStatus(last_order.status).label,
            'form': form,
            'google_api_key': settings.GOOGLE_API_KEY
        }
        return render(request, 'main_app/passenger_new_order.html', context=context)
    else:
        return HttpResponseRedirect('/passenger_start_order/')


def calculate_price(distance, duration):
    print(distance, duration)
    if distance >= 0:
        price = distance * duration
    else:
        raise ValueError
    return price


def distance_two_coordinates(lat1, lon1, lat2, lon2):
    origin = (lat1, lon1)
    destination = (lat2, lon2)
    gmaps = googlemaps.Client(key=GOOGLE_API_KEY)
    duration = gmaps.distance_matrix(origin, destination, mode='driving')["rows"][0]["elements"][0]["duration"]["value"]
    duration_in_hours = duration / 3600
    distance = gmaps.distance_matrix(origin, destination, mode='driving')["rows"][0]["elements"][0]["distance"]["value"]
    distance_in_km = distance / 1000
    return distance_in_km, duration_in_hours


def destination_or_start_name(lat, lon):
    geolocator = GoogleV3(GOOGLE_API_KEY)
    address = geolocator.reverse(str(lat) + "," + str(lon))
    name = address[0]
    return name


@passenger_required
def passenger_start_order(request):
    usr: User = request.user
    passenger = PassengerUser.objects.get(user=usr)
    available_orders = Order.objects.filter(passenger=passenger).filter(
        ~Q(status=OrderStatus.COMPLETED))  # ~ == NOT. Here we return only active orders for passenger
    last_order = available_orders.last()
    if not last_order:
        return HttpResponseRedirect('/passenger_new_order/')
    if request.method == 'POST':
        form = NewOrderForm(request.POST)
        if form.is_valid() and last_order.status == OrderStatus.NEW_ORDER:  # TODO: Need to validate form data; We can put this data only to new order!
            # print(f"BOOOOOOM!!!!! {form.data}")
            start_coords = form.startCoordinates()
            end_coords = form.stopCoordinates()
            last_order.destination_lat = end_coords[0]
            last_order.destination_lon = end_coords[1]
            last_order.start_location_lat = start_coords[0]
            last_order.start_location_lon = start_coords[1]
            lat_d = last_order.destination_lat
            lon_d = last_order.destination_lon
            lat_s = last_order.start_location_lat
            lon_s = last_order.start_location_lon
            destination_name = destination_or_start_name(lat_d, lon_d)
            last_order.destination_name = destination_name
            start_name = destination_or_start_name(lat_s, lon_s)
            last_order.start_name = start_name
            distance, duration = distance_two_coordinates(lat_s, lon_s, lat_d, lon_d)
            last_order.distance = distance
            price = calculate_price(distance, duration)
            if price > last_order.passenger.amount_of_money:
                messages.error(request, 'You did not have enough money to place that order!')
                return redirect('passenger_add_money')
            else:
                last_order.price = float("{:.2f}".format(price))
                last_order.status = OrderStatus.UNASSIGNED
                last_order.save()
        elif 'button' in request.POST:
            action = request.POST['button']
            if last_order.driver is not None:
                if len(Room.objects.filter(user1=last_order.passenger.user, user2=last_order.driver.user)) > 0:
                    room = Room.objects.get(user1=last_order.passenger.user, user2=last_order.driver.user)
                    room.is_current = False
                    room.save()
            if action == 'CANCEL':
                if last_order.status == OrderStatus.UNASSIGNED and last_order.passenger == passenger:
                    last_order.delete()
                if last_order.status == OrderStatus.ASSIGNED and last_order.passenger == passenger:
                    last_order.setStatusAndPayPercent(status = OrderStatus.COMPLETED, percent=50)
                if last_order.status == OrderStatus.IN_PROGRESS and last_order.passenger == passenger:
                    last_order.setStatusAndPayPercent(status = OrderStatus.COMPLETED, percent=80)
            elif action == 'COMPLETE':
                if last_order.status == OrderStatus.IN_PROGRESS and last_order.passenger == passenger:
                    last_order.setStatusAndPayPercent(status = OrderStatus.COMPLETED, percent=100)
                    # TODO: Add redirect on screen to set driver's rate
                    return HttpResponseRedirect(f"/passenger_order/{last_order.id}/")
        else:
            print(f"ERROR!!!\n{form.errors.as_text}")
    if last_order.status == OrderStatus.NEW_ORDER:
        return HttpResponseRedirect('/passenger_new_order/')

    context = {
        'order': last_order,
        'order_status_label': OrderStatus(last_order.status).label,
        'google_api_key': settings.GOOGLE_API_KEY
    }
    return render(request, 'main_app/passenger_new_order.html', context=context)


@passenger_required
def passenger_order(request, order_id):
    order = Order.objects.get(pk=order_id)
    usr: User = request.user
    passenger = PassengerUser.objects.get(user=usr)
    if passenger != order.passenger:  # Passenger can open only his personal orders
        return HttpResponseRedirect('/passenger/')
    context = {
        'order': order,
        'order_status_label': OrderStatus(order.status).label,
        'google_api_key': settings.GOOGLE_API_KEY
    }
    return render(request, 'main_app/passenger_new_order.html', context=context)


@passenger_required
def passenger_rate(request):
    if request.method == 'POST':
        form = request.POST
        rate = float(form['rating'])
        order_id = form['order_id']
        order = Order.objects.get(pk=order_id)
        usr: User = request.user
        passenger = PassengerUser.objects.get(user=usr)
        if order.passenger == passenger:
            rating = order.driver.rating or 0.0
            num = order.driver.number_of_ratings or 0
            new_rating = (rating * num + rate) / (num + 1)
            order.driver.rating = new_rating
            order.driver.number_of_ratings = num + 1
            order.driver.save()
            order.is_rated = True
            order.save()
        print(f"---------!!!!! {order_id} : {rate}")
    return HttpResponseRedirect('/passenger/')


@passenger_required
def passenger_income(request):
    usr: User = request.user
    passenger = PassengerUser.objects.get(user=usr)
    income = f"{passenger.amount_of_money:0.2f}"
    return render(request, 'main_app/passenger_income.html', context={'income': income})


@passenger_required
def passenger_add_money(request):
    usr: User = request.user
    passenger = PassengerUser.objects.get(user=usr)
    income = f"{passenger.amount_of_money:0.2f}"
    if request.method == 'POST':
        form = AddMoneyForm(request.POST)
        if form.is_valid():
            passenger.amount_of_money += form.cleaned_data['amount']
            passenger.save()
            messages.success(request, 'Data was successfully submitted!')
            income = f"{passenger.amount_of_money:0.2f}" # we changed amount_of_money so we need to change income value to render this page correctly
    else:
        form = AddMoneyForm()
        messages.error(request, 'There was a problem while submitting your data! Try again!')
    return render(request, 'main_app/passenger_add_money.html',
                  {'form': form, 'income': income, 'passenger': passenger})


@passenger_required
def passenger_executed_orders(request):
    usr: User = request.user
    passenger = PassengerUser.objects.get(user=usr)
    executed_orders = Order.objects.filter(passenger=passenger).filter(status=OrderStatus.COMPLETED)
    return render(request, 'main_app/passenger_old_orders.html', context={'executed_orders': executed_orders})
