from django.db import models

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=250)
    description = models.TextField()

    def __str__(self):
        return self.name
    
class Participants(models.Model):
    name = models.CharField(max_length=250)
    email = models.EmailField(unique=True, max_length=250)
    # event = models.ManyToManyField(Event)

    def __str__(self):
        return self.name

class Event(models.Model):
    name = models.CharField(max_length=250)
    description = models.TextField()
    # img = models.ImageField(upload_to='event_images', blank=True, default='event_images/default.png')
    event_date = models.DateField()
    event_time = models.TimeField()
    location = models.CharField(max_length=400)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="events", blank=True, null=True)
    participants = models.ManyToManyField(Participants)

    def __str__(self):
        return self.name

class EventImage(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="occavue_images/", blank=True, default='event_images/default.png')

    def __str__(self):
        return f"Image for {self.event.name}"