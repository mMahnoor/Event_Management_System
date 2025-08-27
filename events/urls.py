from django.urls import path
from events.views import dashboard, create_event, add_participant, show_event_detail, show_events, update_event, delete_event, participants, update_participant, delete_participant, category, add_category, update_category, delete_category

urlpatterns = [
    path('dashboard/organizer', dashboard, name='organizer-dashboard'),
    path('create_event/', create_event, name='create_event'),
    path('add_participant/', add_participant, name='add-participant'),
    path('add_category/', add_category, name='add-category'),
    path('update_event/<int:id>/', update_event, name='update-event'),
    path('update_participant/<int:id>/', update_participant, name='update-participant'),
    path('update_category/<int:id>/', update_category, name='update-category'),
    path('delete_event/<int:id>/', delete_event, name='delete-event'),
    path('delete_participant/<int:id>/', delete_participant, name='delete-participant'),
    path('delete_category/<int:id>/', delete_category, name='delete-category'),
    path('view_task/', show_events, name='view-task'),
    path('event_detail/', show_event_detail, name='event-detail'),
    path('participants/', participants, name='participants'),
    path('category/', category, name='category'),
    # path('search_events/', search_events, name='search-events'),
    # path('search_form/', search_form, name='search-form'),
]