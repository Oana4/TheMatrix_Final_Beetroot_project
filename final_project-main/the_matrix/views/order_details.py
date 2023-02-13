from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from ..models import User, Order, OrderStatus

def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

@login_required
def get_order_details(request):
    # request should be ajax and method should be GET.
    if is_ajax(request) and request.method == "GET":
        # get the nick name from the client side.
        order_id = request.GET.get("order_id", None)
        order = Order.objects.get(pk=order_id)
        usr: User = request.user

        # check for the nick name in the database.
        if order.passenger.user == usr or order.driver.user == usr or order.status == OrderStatus.UNASSIGNED:
            # if nick_name found return not valid new friend
            return JsonResponse({"order_status": order.status}, status = 200)
        else:
            # we can't show of other orders.
            return JsonResponse({}, status = 400)

    return JsonResponse({}, status = 400)