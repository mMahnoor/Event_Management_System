from django.shortcuts import render
from events.models import Event
from django.db.models import Q

# Create your views here.
def home(request):
    type = request.GET.get('type', 'recents')
    base_query = Event.objects.select_related('category').prefetch_related('images')
    # events
    if type=="search":
        keyword = request.GET.get("keyword")
        events = base_query.filter(Q(name__icontains=keyword)|Q(location__icontains=keyword)).only("name", "description", "location", "event_date", "event_time", "category")
        title="Search result"
    else:
        events = base_query.order_by("event_date").only("name", "description", "location", "event_date", "event_time", "category")[:10]
        title="Most Recent"

    for event in events:
        event.first_image = event.images.all()[0] if event.images.all() else None

    return render(request, "Home/hero_section.html", {"events":events, "title":title})

def no_permission(request):
    return render(request, 'no_permission.html')