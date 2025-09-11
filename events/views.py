from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from events.forms import EventModelForm, EventImageForm, CategoryModelForm, RSVPModelForm
from django.contrib.auth.forms import UserChangeForm
from events.models import Event, Category, EventImage, RSVP
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Sum, Q
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView
from django.views.generic import DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils.decorators import method_decorator
from django.utils.timezone import localdate
from users.views import is_admin
from users.forms import CustomUserChangeForm
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your views here.

# test functions
def is_organizer(user):
    return user.groups.filter(name='Organizer').exists()

def organizer_or_admin(user):
    roles = set(user.groups.values_list("name", flat=True))
    return "Admin" in roles or "Organizer" in roles

@user_passes_test(organizer_or_admin, login_url='no-permission')
def category(request):
    categories = Category.objects.all().order_by('id')
    context = {"categories":categories}
    return render(request, "Category/category.html", context)

@user_passes_test(is_organizer, login_url='no-permission')
def dashboard(request):
    type = request.GET.get('type', 'today')
    counts = Event.objects.aggregate(
        total_events=Count('id', distinct=True),
        past_events=Count('id', filter=Q(event_date__lt=localdate()), distinct=True),
        upcoming_events=Count('id', filter=Q(event_date__gt=localdate()), distinct=True),
        total_participants=Count('participants', distinct=True),
    )

    # Retriving event data
    base_query = Event.objects.select_related('category', 'organizer').prefetch_related('participants','images')
    participants=[]
    if type == 'past_events':
        events = base_query.filter(event_date__lt=localdate())
        title = "Past Events"
    elif type == 'upcoming_events':
        events = base_query.filter(event_date__gt=localdate())
        title = "Upcoming Events"
    elif type == 'total_participants':
        participants = Event.objects.select_related("organizer").annotate(total_rsvps=Count('rsvp'))
        events = []
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
        "participant_headers": ["Name", "Organized By", "Total RSVPs"],
        "categories":categories,
    }
    return render(request, "dashboard/organizer_dashboard.html", context)

@user_passes_test(organizer_or_admin, login_url='no-permission')
def create_event(request):
    event_form = EventModelForm()
    image_form = EventImageForm()
    if request.method == "POST":
        event_form = EventModelForm(request.POST, request.FILES)
        image_form = EventImageForm(request.POST, request.FILES)
        if event_form.is_valid():

            """ For Model Form Data """
            event = event_form.save(commit=False)
            print('organizer:',event.organizer," | ",request.user)
            event.organizer = request.user
            event.save()
            print('organizer-after:',event.organizer," | ",request.user)
            images = request.FILES.getlist("image")
            for img in images:
                image_instance = EventImage(image=img, event=event)
                image_instance.save()

            messages.success(request, "Event Created Successfully")
            return redirect('create-event')

    context = {"form": event_form, "image_form": image_form, "form_title":"Create a New Event"}
    return render(request, "event_form.html", context)

@method_decorator(user_passes_test(organizer_or_admin, login_url="no-permission"), name="dispatch")
class CreateEventView(LoginRequiredMixin, CreateView):
    model = Event
    form_class = EventModelForm
    template_name = "event_form.html"
    success_url = reverse_lazy("create-event") 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["image_form"] = kwargs.get("image_form", EventImageForm())
        context["form_title"] = "Create a New Event"
        return context

    def form_valid(self, form):
        event = form.save(commit=False)
        event.organizer = self.request.user
        event.save()

        images = self.request.FILES.getlist("image")
        for img in images:
            EventImage.objects.create(image=img, event=event)

        messages.success(self.request, "Event Created Successfully")
        return redirect("create-event")

    def form_invalid(self, form):
        context = self.get_context_data(form=form, image_form=EventImageForm(self.request.POST, self.request.FILES))
        return self.render_to_response(context)

@user_passes_test(is_admin, login_url='no-permission')
def add_rsvp_using_form(request):
    form = RSVPModelForm()
    if request.method == "POST":
        form = RSVPModelForm(request.POST)
        if form.is_valid():            
            form.save()
            messages.success(request, "Participant added successfully!")
        else:
            messages.warning(request, "The user has already RSVP'd for this event.")
            print(form.errors)
        return redirect('add-participant')
    context = {"form": form, "form_title":"Add New Participant"}
    return render(request, "event_form.html", context)

@login_required
def add_rsvp_on_button_click(request):
    if request.method == "POST":
        form = RSVPModelForm(request.POST)
        if form.is_valid():
            form.save() 
            messages.success(request, "You have successfully RSVP'd.")
        else:
            messages.warning(request, "You already RSVP'd for this event.")
            print(form.errors)
    return redirect(request.headers.get("REFERER"))

@user_passes_test(organizer_or_admin, login_url='no-permission')
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
@user_passes_test(organizer_or_admin, login_url='no-permission')
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

@user_passes_test(is_admin, login_url='no-permission')
def update_user(request, id):
    user = User.objects.get(pk=id)
    form = CustomUserChangeForm(instance=user)
    
    if request.method == "POST":
        form = CustomUserChangeForm(request.POST, instance=user)
        if form.is_valid():

            """ For Model Form Data """
            user = form.save()
            
            messages.success(request, "Info updated successfully!")
            return redirect('update-user', id)
    context = {"form": form, "form_title":"Update Participant Info"}
    return render(request, "event_form.html", context)

@user_passes_test(organizer_or_admin, login_url='no-permission')
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

@user_passes_test(is_admin, login_url='no-permission')
def update_rsvp(request, id):
    rsvp = RSVP.objects.get(id=id)
    form = RSVPModelForm(instance=rsvp)
    
    if request.method == "POST":
        form = RSVPModelForm(request.POST, instance=rsvp)
        if form.is_valid():

            """ For Model Form Data """
            rsvp = form.save()
            
            messages.success(request, "rsvp updated successfully!")
            return redirect('update-rsvp', id)
    context = {"form": form, "form_title":"Update RSVP"}
    return render(request, "event_form.html", context)


# Delete Event
@user_passes_test(organizer_or_admin, login_url='no-permission')
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

@method_decorator(user_passes_test(organizer_or_admin, login_url="no-permission"), name="dispatch")
class DeleteEventView(DeleteView):
    model = Event
    template_name = "info.html" 
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        event_name = str(self.object)
        self.object.delete()
        messages.success(request, f"Event '{event_name}' deleted successfully.")
        return render(request, self.template_name)

    def get(self, request, *args, **kwargs):
        messages.error(request, "Something went wrong!")
        return render(request, self.template_name)

@user_passes_test(is_admin, login_url='no-permission')
def delete_user(request, id):
    if request.method == "POST":
        user = User.objects.get(pk=id)
        user.delete()
        messages.success(request, "User deleted successfully.")
    else:
        messages.error(request, 'Something went wrong!')
    return render(request, "info.html")

@user_passes_test(organizer_or_admin, login_url='no-permission')
def delete_category(request, id):
    if request.method == "POST":
        category = Category.objects.get(id=id)
        category.delete()
        messages.success(request, "Category deleted successfully.")
    else:
        messages.error(request, 'Something went wrong!')
    return render(request, "info.html")

@user_passes_test(is_admin, login_url='no-permission')
def delete_rsvp(request, id):
    if request.method == "POST":
        rsvp = RSVP.objects.get(pk=id)
        rsvp.delete()
        messages.success(request, "RSVP deleted successfully.")
    else:
        messages.error(request, 'Something went wrong!')
    return render(request, "info.html")


# Show Events
def show_events(request):
    events = Event.objects.annotate(
        num_events=Count('event')).order_by('num_events')
    return render(request, "show_events.html", {"event_list": events})

@user_passes_test(organizer_or_admin, login_url='no-permission')
def show_event_detail(request):
    id = request.GET.get('id')
    event = Event.objects.prefetch_related('participants','images').get(pk=id)
    context = {"detail": event}
    return render(request, "event_detail.html", context)

# Show RSVPs
@user_passes_test(is_admin, login_url='no-permission')
def show_participants(request):
    rsvps = RSVP.objects.select_related("user", "event__category", "event__organizer")
    context = {"rsvp_list":rsvps}
    return render(request, "admin/participants_list.html", context)

def browse_events(request):
    type = request.GET.get("type", "all")
    base_query = Event.objects.select_related('category').prefetch_related('images')

    if type=="search":
        keyword = request.GET.get("keyword")
        category = request.GET.get('category')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        location = request.GET.get('location')
        filters = Q()
        if keyword:
            filters &= Q(name__icontains=keyword)|Q(location__icontains=keyword)
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
        title="Search result"
    else:
        events = base_query.all()
        title = "All Events"
    for event in events:
        event.first_image = event.images.all()[0] if event.images.all() else None
    categories = Category.objects.all()
    context = {"events":events, "categories":categories, "title": title}
    return render(request, "browse_events.html", context)

class BrowseEventsView(ListView):
    model = Event
    template_name = "browse_events.html"
    context_object_name = "events"

    def get_queryset(self):
        type = self.request.GET.get("type", "all")
        base_query = Event.objects.select_related("category").prefetch_related("images")

        if type == "search":
            keyword = self.request.GET.get("keyword")
            category = self.request.GET.get("category")
            start_date = self.request.GET.get("start_date")
            end_date = self.request.GET.get("end_date")
            location = self.request.GET.get("location")

            filters = Q()
            if keyword:
                filters &= Q(name__icontains=keyword) | Q(location__icontains=keyword)
            if category:
                filters &= Q(category__name__icontains=category)
            if location:
                filters &= Q(location__icontains=location)
            if start_date and end_date:
                filters &= Q(event_date__range=[start_date, end_date])
            elif start_date:
                filters &= Q(event_date__gt=start_date)
            elif end_date:
                filters &= Q(event_date__lt=end_date)

            queryset = base_query.filter(filters)
            self.title = "Search result"
        else:
            queryset = base_query.all()
            self.title = "All Events"

        for event in queryset:
            event.first_image = event.images.first()

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        context["title"] = getattr(self, "title", "All Events")
        return context

# search form
# def search_form(request):
#     categories = Category.objects.all()
#     return render(request, "search_form.html", {"categories":categories})

# Search Events