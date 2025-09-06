from django.contrib import admin
from events.models import Event, Category, EventImage

# Register your models here.
admin.site.register(Event)
admin.site.register(Category)
