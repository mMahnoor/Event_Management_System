from django.shortcuts import render, redirect
from django.contrib.auth.models import Group
from django.contrib.auth import login, logout
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse_lazy
from users.forms import CustomRegisterForm, LoginForm, CreateGroupForm, EditProfileForm, CustomPasswordChangeForm,CustomPasswordResetForm, CustomPasswordResetConfirmForm
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Prefetch
from events.models import Event, EventImage, RSVP, Category
from django.db.models import Count, Q
from django.utils.timezone import localdate
from django.utils.safestring import mark_safe
from django.views.generic import ListView, FormView, TemplateView, UpdateView
from django.contrib.auth.views import PasswordChangeView, PasswordResetView, PasswordResetConfirmView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your views here.
def sign_up(request):
    if request.method == 'GET':
        form = CustomRegisterForm()
    if request.method == 'POST':
        form = CustomRegisterForm(request.POST) 
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data.get('password'))
            user.is_active = False
            user.save()
            # messages.success(
            #     request, 'A Confirmation mail sent. Please check your email')
            # return redirect('sign-in')
        else:
            print("Form is not valid")

    return render(request, "registration/sign_up.html", {"form":form})

class SignUpView(FormView):
    template_name = "registration/sign_up.html"
    form_class = CustomRegisterForm
    success_url = reverse_lazy("sign-in")

    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data.get("password"))
        user.is_active = False
        user.save()

        messages.success(
            self.request,
            "An Account activation mail is sent. Please check your email."
        )

        return super().form_valid(form)

    def form_invalid(self, form):
        print("Form is not valid:", form.errors)
        return super().form_invalid(form)

def sign_in(request):
    if(request.method == 'GET'):
        form = LoginForm()

    if(request.method == 'POST'):
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            print("suer_cred:",user)
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Please enter correct username/password")
        
    return render(request, 'registration/sign_in.html', {"form": form})

@login_required
def sign_out(request):
    if(request.method == 'POST'):
        logout(request)
        return redirect('sign-in')

# User account activation
def activate_user(request, user_id, token):
    try:
        user = User.objects.get(id=user_id)
        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return redirect('sign-in')
        else:
            return HttpResponse('Invalid Id or token')

    except User.DoesNotExist:
        return HttpResponse('User not found')

# Test functions  
def is_admin(user):
    return user.groups.filter(name='Admin').exists()

def is_user(user):
    return user.groups.filter(name='User').exists()

@user_passes_test(is_admin, login_url='no-permission')
def admin_dashboard(request):
    type = request.GET.get("type", "all_users")
    counts = Event.objects.select_related('category','organizer').prefetch_related('participants','images').aggregate(
        total_events=Count('id', distinct=True),
        upcoming_events=Count('id', filter=Q(event_date__gt=localdate()), distinct=True),
    )
    counts["rsvp_count"] = RSVP.objects.count()
    admin_counts = User.objects.aggregate(
        total_users=Count('id', distinct=True),
    )
    counts.update(admin_counts)
    users = User.objects.prefetch_related(
        Prefetch('groups', queryset=Group.objects.all(), to_attr='all_groups')
    ).all()

    print(users)

    for user in users:
        if user.all_groups:
            user.group_name = user.all_groups[0].name
        else:
            user.group_name = 'No Group Assigned'
    events=[]
    if type=="rsvps":
        events = Event.objects.select_related('category','organizer').annotate(rsvp_count=Count("participants"))
        title="RSVPs"
        head_list = ['SL', 'Event Name', 'Organized By', 'Total RSVPs']
    elif type=="upcoming":
        events = Event.objects.select_related('organizer').filter(Q(event_date__gt=localdate()))
        title="Events"
        head_list = ['SL', 'Event Name', 'Organized By', 'Event date', 'Event time']
    elif type=="all":
        events = Event.objects.select_related('organizer')
        title="Events"
        head_list = ['SL', 'Event Name', 'Organized By', 'Event date', 'Event time']
    else:
        title="All Users"
        head_list = ['SL', 'Full name',	'Username',	'Email', 'User ID',	'Current Role',	'Action']
    context={
        "users": users,
        "events": events,
        "counts":counts,
        "title": title,
        "head_list": head_list
    }
    return render(request, 'dashboard/admin_dashboard.html', context)

@user_passes_test(is_user, login_url='no-permission')
def user_dashboard(request):
    user = request.user
    
    base_query = user.rsvp_events.select_related('category', 'organizer').prefetch_related(
            Prefetch('images', queryset=EventImage.objects.order_by('id'), to_attr='prefetched_images')
        )
    title="RSVP'd Events"

    # looking for search keys
    type = request.GET.get("type", "all")
    if(type == "search"):
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
    else:
        events = base_query.all()

    for event in events:
        event.first_image = event.prefetched_images[0] if event.prefetched_images else None

    # category retrieval
    categories = Category.objects.all()

    context = {"rsvp_list":events, "total_rsvps":events.count(), "events":events, "title":title, "categories":categories}
    return render(request, "dashboard/user_dashboard.html", context)


@user_passes_test(is_admin, login_url='no-permission')
def create_group(request):
    form = CreateGroupForm()
    if request.method == 'POST':
        form = CreateGroupForm(request.POST)

        if form.is_valid():
            group = form.save()
            messages.success(request, mark_safe(f"Group <b>{group.name}</b> has been created successfully"))
            return redirect('group-list')

    return render(request, 'Widgets/formModal.html', {'form': form})

@user_passes_test(is_admin, login_url='no-permission')
def group_list(request):
    form = CreateGroupForm()
    groups = Group.objects.prefetch_related('permissions').all()
    return render(request, 'admin/group_list.html', {'groups': groups, 'form':form})

@user_passes_test(is_admin, login_url='no-permission')
def delete_group(request, group_id):
    group = Group.objects.get(id=group_id)
    if group.user_set.exists():
        messages.error(request, f'Cannot delete group "{group.name}" because it has users assigned.')
    else:
        group.delete()
        messages.success(request, f'Group "{group.name}" has been deleted.')
    return redirect('group-list')

@user_passes_test(is_admin, login_url='no-permission')
def admin_events_list(request):
    type = request.GET.get("type", "all")
    base_query = Event.objects.select_related('category').prefetch_related('participants','images')
    title="All Events"
    if(type == "search"):
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
    else:
        events = base_query.all()

    for event in events:
        event.first_image = event.images.all()[0] if event.images.all() else None

    categories = Category.objects.all()
    context = {
        "title": title,
        "events": events,
        "categories": categories
    }

    return render(request, "admin/events_list.html", context)

@method_decorator(user_passes_test(is_admin, login_url="no-permission"), name="dispatch")
class AdminEventsListView(LoginRequiredMixin, ListView):
    model = Event
    template_name = "admin/events_list.html"
    context_object_name = "events"

    def test_func(self):
        return is_admin(self.request.user)

    def get_queryset(self):
        type = self.request.GET.get("type", "all")
        base_query = Event.objects.select_related("category").prefetch_related("participants", "images")

        if type == "search":
            category = self.request.GET.get("category")
            start_date = self.request.GET.get("start_date")
            end_date = self.request.GET.get("end_date")
            location = self.request.GET.get("location")

            filters = Q()
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
            self.title = "Search Results"
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
    
# Profile
class ProfileView(TemplateView):
    template_name = 'accounts/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        context['username'] = user.username
        context['email'] = user.email
        context['name'] = user.get_full_name()
        context['phone'] = user.phone
        context['profile_image'] = user.profile_image

        context['member_since'] = user.date_joined
        context['last_login'] = user.last_login
        return context
    
class EditProfileView(UpdateView):
    model = User
    form_class = EditProfileForm
    template_name = 'accounts/edit_profile_form.html'
    context_object_name = 'form'

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        form.save()
        return redirect('profile')

# Change password
class ChangePasswordView(PasswordChangeView):
    template_name = 'accounts/password_change.html'
    form_class = CustomPasswordChangeForm

# Reset Password
class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = 'registration/reset_password.html'
    success_url = reverse_lazy('sign-in')
    html_email_template_name = 'registration/custom_reset_email.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['protocol'] = 'https' if self.request.is_secure() else 'http'
        context['domain'] = self.request.get_host()
        print('Reset bug: ',context)
        return context

    def form_valid(self, form):
        messages.success(
            self.request, 'A Reset email will be sent within few minutes. Please check your email...')
        return super().form_valid(form)


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = CustomPasswordResetConfirmForm
    template_name = 'registration/reset_password.html'
    success_url = reverse_lazy('sign-in')

    def form_valid(self, form):
        messages.success(
            self.request, 'Password is reset successfully')
        return super().form_valid(form)

