from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=250)
    description = models.TextField()

    def __str__(self):
        return self.name
    
class Event(models.Model):
    name = models.CharField(max_length=250)
    description = models.TextField()
    event_date = models.DateField()
    event_time = models.TimeField()
    location = models.CharField(max_length=400)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="events", blank=True, null=True)
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="organized_events", default=1)
    participants = models.ManyToManyField(User, through="RSVP", related_name="rsvp_events")

    def __str__(self):
        return self.name
    
class RSVP(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["event", "user"], name="unique_rsvp_pairs"
            )
        ]

class EventImage(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="occavue_images/", blank=True, default='event_images/default.png')

    def __str__(self):
        return f"Image for {self.event.name}"