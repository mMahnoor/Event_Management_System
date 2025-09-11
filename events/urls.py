from django.urls import path
from events.views import dashboard, create_event, show_event_detail, show_events, update_event, delete_event, show_participants, add_rsvp_using_form, add_rsvp_on_button_click, update_rsvp, delete_rsvp, update_user, delete_user, category, add_category, update_category, delete_category, browse_events, CreateEventView, BrowseEventsView, DeleteEventView

urlpatterns = [
    path('dashboard/organizer', dashboard, name='organizer-dashboard'),
    # path('dashboard/admin', dashboard, name='admin-dashboard'),
    path('create_event/', CreateEventView.as_view(), name='create-event'),
    path('add_participant/', add_rsvp_using_form, name='add-participant'),
    path('add_rsvp/', add_rsvp_on_button_click, name='add-rsvp'),
    path('add_category/', add_category, name='add-category'),
    path('update_event/<int:id>/', update_event, name='update-event'),
    path('update_user/<int:id>/', update_user, name='update-user'),
    path('update_category/<int:id>/', update_category, name='update-category'),
    path('update_rsvp/<int:id>/', update_rsvp, name='update-rsvp'),
    path('delete_event/<int:pk>/', DeleteEventView.as_view(), name='delete-event'),
    path('delete_user/<int:id>/', delete_user, name='delete-user'),
    path('delete_category/<int:id>/', delete_category, name='delete-category'),
    path('delete_rsvp/<int:id>/', delete_rsvp, name='delete-rsvp'),
    path('view_task/', show_events, name='view-task'),
    path('event_detail/', show_event_detail, name='event-detail'),
    path('participants/', show_participants, name='participants'),
    path('category/', category, name='category'),
    path('browse_event/', BrowseEventsView.as_view(), name='browse-event'),
    # path('search_events/', search_events, name='search-events'),
    # path('search_form/', search_form, name='search-form'),
]