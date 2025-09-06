from django.shortcuts import render, redirect
from django.contrib.auth.models import User, Group
from django.contrib.auth import login, logout
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required, user_passes_test
from users.forms import CustomRegisterForm, LoginForm, CreateGroupForm
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Prefetch
from events.models import Event, EventImage, RSVP, Category
from django.db.models import Count, Q
from django.utils.timezone import localdate
from django.utils.safestring import mark_safe

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

# @user_passes_test(is_admin, login_url='no-permission')
# def assign_role(request, user_id):
#     user = User.objects.get(id=user_id)
#     form = AssignRoleForm()

#     if request.method == 'POST':
#         form = AssignRoleForm(request.POST)
#         if form.is_valid():
#             role = form.cleaned_data.get('role')
#             user.groups.clear()  # Remove old roles
#             user.groups.add(role)
#             messages.success(request, f"User {user.username} has been assigned to the {role.name} role")
#             return redirect('admin-dashboard')

#     return render(request, 'Widgets/formModal.html', {'form': form})

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