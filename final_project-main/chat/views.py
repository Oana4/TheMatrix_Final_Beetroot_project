from django.http.response import HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from the_matrix.models import User

from .models import Room, Message


@login_required
def rooms(request):
    if request.user.is_superuser:
        rooms_admin = Room.objects.filter(user2=None)
        return render(request, 'chat_templates/rooms.html', {'rooms1': rooms_admin})

    else:
        rooms1 = Room.objects.filter(user1=request.user)
        rooms2 = Room.objects.filter(user2=request.user)
        return render(request, 'chat_templates/rooms.html', {'rooms1': rooms1, 'rooms2': rooms2})


@login_required
def room(request, id):

    room = Room.objects.get(id=id)
    messages = Message.objects.filter(room=room)

    if not request.user.is_superuser:
        if room.user1 != request.user and room.user2 != request.user:
            return redirect('rooms')

    return render(request, 'chat_templates/room.html', {'room': room, 'messages': messages})
