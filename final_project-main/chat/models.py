from django.db import models
from the_matrix.models import User


class Room(models.Model):

    is_current = models.BooleanField(default=False)
    user1 = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='user1')
    user2 = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='user2')


class Message(models.Model):
    room = models.ForeignKey(Room, related_name='messages', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='messages', on_delete=models.CASCADE)
    content = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('date_added',)
