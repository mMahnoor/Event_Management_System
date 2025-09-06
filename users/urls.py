from django.urls import path
from users.views import sign_up, sign_in, sign_out, activate_user, admin_dashboard, user_dashboard, create_group, group_list, admin_events_list, delete_group

urlpatterns = [
    path("sign-up/", sign_up, name="sign-up"),
    path("sign-in/", sign_in, name="sign-in"),
    path('sign-out/', sign_out, name='sign-out'),
    path('activate/<int:user_id>/<str:token>/', activate_user),
    path('user/dashboard/', user_dashboard, name='user-dashboard'),
    path('admin/dashboard/', admin_dashboard, name='admin-dashboard'),
    # path('admin/<int:user_id>/assign-role/', assign_role, name='assign-role'),
    path('admin/create-group/', create_group, name='create-group'),
    path('admin/group-list/', group_list, name='group-list'),
    path('admin/events-list/', admin_events_list, name='events-list'),
    path('admin/delete-group/<int:group_id>/', delete_group, name='delete-group'),
]
