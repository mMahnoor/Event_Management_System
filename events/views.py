from django.shortcuts import render, redirect
from events.forms import EventModelForm, EventImageForm, ParticipantModelForm, CategoryModelForm
from events.models import Event, Participants, Category
from events.models import EventImage
from django.contrib import messages
from django.db.models import Count, Sum, Q
from django.utils.timezone import localdate

# Create your views here.
def home(request):
    type = request.GET.get('type', 'recents')
    base_query = Event.objects.prefetch_related('images')
    # events
    if type=="search":
        keyword = request.GET.get("keyword")
        events = base_query.filter(Q(name__icontains=keyword)|Q(location__icontains=keyword)).only("name", "description", "location", "event_date", "event_time")
        title="Search result"
    else:
        events = base_query.order_by("event_date").only("name", "description", "location", "event_date", "event_time")[:10]
        title="Most Recent"

    for event in events:
        event.first_image = event.images.all()[0] if event.images.all() else None

    return render(request, "Home/hero_section.html", {"events":events, "title":title})

def participants(request):
    participants = Participants.objects.all().order_by('id')
    context = {"participants":participants}
    return render(request, "Participants/participants.html", context)

def category(request):
    categories = Category.objects.all().order_by('id')
    context = {"categories":categories}
    return render(request, "Category/category.html", context)

def dashboard(request):
    type = request.GET.get('type', 'today')
    counts = Event.objects.aggregate(
        total_events=Count('id', distinct=True),
        past_events=Count('id', filter=Q(event_date__lt=localdate()), distinct=True),
        upcoming_events=Count('id', filter=Q(event_date__gt=localdate()), distinct=True),
        total_participants=Count('participants', distinct=True),
    )

    # Retriving event data
    base_query = Event.objects.select_related('category').prefetch_related('participants','images')
    participants=[]
    if type == 'past_events':
        events = base_query.filter(event_date__lt=localdate())
        title = "Past Events"
    elif type == 'upcoming_events':
        events = base_query.filter(event_date__gt=localdate())
        title = "Upcoming Events"
    elif type == 'total_participants':
        total_events = Participants.objects.annotate(total_events=Count('event')).filter(total_events__gt=0)
        events = []
        participants = total_events
        title = "Participants"
        print("hi:", participants)
    elif type == 'all':
        events = base_query.all()
        title = "All Events"
    elif type == 'today':
        events = base_query.filter(event_date=localdate())
        title = "Today's Events"
    elif type == 'search':
        category = request.GET.get('category')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        location = request.GET.get('location')
        filters = Q()
        if category:
            filters &= Q(category__name__icontains=category)
        if location:
            filters &= Q(location__icontains=location)
        if start_date and end_date:
            filters &= Q(event_date__range=[start_date, end_date]) 
        if start_date and not end_date:
            filters &= Q(event_date__gt=start_date)
        if not start_date and end_date:
            filters &= Q(event_date__lt=end_date)

        events = base_query.filter(filters)
        title = "Search Results"

    for event in events:
        event.first_image = event.images.all()[0] if event.images.all() else None

    # category retrieval
    categories = Category.objects.all()

    context = {
        "title": title,
        "events": events,
        "counts": counts,
        "participants": participants,
        "participant_headers": ["Name", "Email", "Total Events"],
        "categories":categories,
    }
    return render(request, "dashboard/organizer_dashboard.html", context)

def create_event(request):
    event_form = EventModelForm()
    image_form = EventImageForm()
    if request.method == "POST":
        event_form = EventModelForm(request.POST, request.FILES)
        image_form = EventImageForm(request.POST, request.FILES)
        if event_form.is_valid():

            """ For Model Form Data """
            event = event_form.save()
            images = request.FILES.getlist("image")
            for img in images:
                image_instance = EventImage(image=img, event=event)
                image_instance.save()

            messages.success(request, "Event Created Successfully")
            return redirect('create_event')

    context = {"form": event_form, "image_form": image_form, "form_title":"Create a New Event"}
    return render(request, "event_form.html", context)

def add_participant(request):
    form = ParticipantModelForm()
    if request.method == "POST":
        form = ParticipantModelForm(request.POST, request.FILES)
        if form.is_valid():

            """ For Model Form Data """
            participant = form.save()
            
            messages.success(request, "Participant added successfully!")
            return redirect('add-participant')

    context = {"form": form, "form_title":"Add New Participant"}
    return render(request, "event_form.html", context)

def add_category(request):
    form = CategoryModelForm()
    if request.method == "POST":
        form = CategoryModelForm(request.POST, request.FILES)
        if form.is_valid():

            """ For Model Form Data """
            category = form.save()
            
            messages.success(request, "Category added successfully!")
            return redirect('add-category')

    context = {"form": form, "form_title":"Create a Category"}
    return render(request, "event_form.html", context)

# Update Event
def update_event(request, id):
    event = Event.objects.prefetch_related("participants", "images").get(id=id)
    images = event.images.all()
    image_form = EventImageForm()
    
    if request.method == "POST":
        event_form = EventModelForm(request.POST, instance=event)
        if event_form.is_valid():

            """ For Model Form Data """
            event = event_form.save()
            new_images = request.FILES.getlist("image")
            for img in new_images:
                image_instance = EventImage(image=img, event=event)
                image_instance.save()

            messages.success(request, "Event updated successfully!")
            return redirect('update-event', id)
    else: 
        event_form = EventModelForm(instance=event)
    context = {"form": event_form,"image_form": image_form, "images":images, "form_title":"Update Event"}
    return render(request, "event_form.html", context)

def update_participant(request, id):
    participant = Participants.objects.get(id=id)
    form = ParticipantModelForm(instance=participant)
    
    if request.method == "POST":
        form = ParticipantModelForm(request.POST, instance=participant)
        if form.is_valid():

            """ For Model Form Data """
            participant = form.save()
            
            messages.success(request, "Info updated successfully!")
            return redirect('update-participant', id)
    context = {"form": form, "form_title":"Update Participant Info"}
    return render(request, "event_form.html", context)

def update_category(request, id):
    category = Category.objects.get(id=id)
    form = CategoryModelForm(instance=category)
    
    if request.method == "POST":
        form = CategoryModelForm(request.POST, instance=category)
        if form.is_valid():

            """ For Model Form Data """
            category = form.save()
            
            messages.success(request, "Category updated successfully!")
            return redirect('update-category', id)
    context = {"form": form, "form_title":"Update Category"}
    return render(request, "event_form.html", context)

# Delete Event
def delete_event(request, id):
    print("hello del!")
    if request.method == "POST":
        event = Event.objects.get(id=id)
        print(event)
        event.delete()
        messages.success(request, "Event deleted successfully.")
    else:
        messages.error(request, 'Something went wrong!')
    return render(request, "info.html")

def delete_participant(request, id):
    if request.method == "POST":
        participant = Participants.objects.get(id=id)
        participant.delete()
        messages.success(request, "Participant deleted successfully.")
    else:
        messages.error(request, 'Something went wrong!')
    return render(request, "info.html")

def delete_category(request, id):
    if request.method == "POST":
        category = Category.objects.get(id=id)
        category.delete()
        messages.success(request, "Category deleted successfully.")
    else:
        messages.error(request, 'Something went wrong!')
    return render(request, "info.html")


# Show Events
def show_events(request):
    events = Event.objects.annotate(
        num_events=Count('event')).order_by('num_events')
    return render(request, "show_events.html", {"event_list": events})

def show_event_detail(request):
    id = request.GET.get('id')
    event = Event.objects.prefetch_related('participants','images').get(pk=id)
    context = {"detail": event}
    return render(request, "event_detail.html", context)

# search form
# def search_form(request):
#     categories = Category.objects.all()
#     return render(request, "search_form.html", {"categories":categories})

# Search Events