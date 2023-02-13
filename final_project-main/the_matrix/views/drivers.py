from django.contrib.auth import login
from django.views.generic import CreateView
from django.shortcuts import render, redirect
from django.conf import settings

from ..forms import NewDriverForm
from ..models import User, Order, DriverUser, OrderStatus
from ..decorators import driver_required
from chat.models import Room


class DriverSignUpView(CreateView):
    model = User
    form_class = NewDriverForm
    template_name = 'main_app/register_driver.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'driver'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('driver_page')


@driver_required
def driver_page(request):
    usr: User = request.user
    driver = DriverUser.objects.get(user=usr)
    driver_orders = Order.objects.filter(driver=driver).all()
    last_order = driver_orders.last()
    return render(request, 'main_app/driver_page.html', context={'order': last_order})


@driver_required
def driver_available_orders(request):
    unassigned_orders = Order.objects.filter(status=OrderStatus.UNASSIGNED)
    return render(request, 'main_app/driver_orders.html', context={'unassigned_orders': unassigned_orders})


@driver_required
def driver_executed_orders(request):
    usr: User=request.user
    drv = DriverUser.objects.get(user=usr)
    executed_orders = Order.objects.filter(driver=drv).filter(status=OrderStatus.COMPLETED)
    return render(request, 'main_app/driver_orders.html', context={'executed_orders': executed_orders})


@driver_required
def driver_income(request):
    usr: User=request.user
    drv = DriverUser.objects.get(user=usr)
    income = f"{drv.amount_of_money:0.2f}"
    return render(request, 'main_app/driver_income.html', context={'income': income})


@driver_required
def driver_order(request, order_id):
    order = Order.objects.get(pk=order_id)
    if request.method == 'POST':
        action = request.POST['button']
        usr: User=request.user
        drv = DriverUser.objects.get(user=usr)
        print(f"ACT: {action}")
        if action == 'ASSIGN':
            if order.status == OrderStatus.UNASSIGNED and not order.driver:
                order.status = OrderStatus.ASSIGNED
                order.driver = drv
                order.save()
                print(f"Order OK")
                if len(Room.objects.filter(user1=order.passenger.user, user2=order.driver.user)) > 0:
                    room = Room.objects.get(user1=order.passenger.user, user2=order.driver.user)
                    room.is_current = True
                    room.save()
                else:
                    Room.objects.create(user1=order.passenger.user, user2=order.driver.user, is_current=True)

        elif action == 'CANCEL':
            if (order.status == OrderStatus.ASSIGNED or order.status == OrderStatus.IN_PROGRESS) and order.driver == drv:
                room = Room.objects.get(user1=order.passenger.user, user2=order.driver.user)
                order.status = OrderStatus.UNASSIGNED
                order.driver = None
                order.save()
                room.is_current = False
                room.save()
        elif action == 'START':
            usr: User=request.user
            drv = DriverUser.objects.get(user=usr)
            if order.status == OrderStatus.ASSIGNED and order.driver == drv:
                order.status = OrderStatus.IN_PROGRESS
                order.save()
    context = {
        'google_api_key': settings.GOOGLE_API_KEY,
        'order': order,
        'order_status_label': OrderStatus(order.status).label,
        }
    return render(request, 'main_app/driver_order.html', context=context)

