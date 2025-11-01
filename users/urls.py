from django.urls import path
from users.views import ProfileView, sign_in, sign_out, activate_user, admin_dashboard, user_dashboard, create_group, group_list, admin_events_list, delete_group, AdminEventsListView, SignUpView, EditProfileView, ChangePasswordView,CustomPasswordResetView, CustomPasswordResetConfirmView
from django.contrib.auth.views import PasswordChangeDoneView

urlpatterns = [
    path("sign-up/", SignUpView.as_view(), name="sign-up"),
    path("sign-in/", sign_in, name="sign-in"),
    path('sign-out/', sign_out, name='sign-out'),
    path('activate/<int:user_id>/<str:token>/', activate_user),
    path('user/dashboard/', user_dashboard, name='user-dashboard'),
    path('admin/dashboard/', admin_dashboard, name='admin-dashboard'),
    # path('admin/<int:user_id>/assign-role/', assign_role, name='assign-role'),
    path('admin/create-group/', create_group, name='create-group'),
    path('admin/group-list/', group_list, name='group-list'),
    path('admin/events-list/', AdminEventsListView.as_view(), name='events-list'),
    path('admin/delete-group/<int:group_id>/', delete_group, name='delete-group'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('edit-profile/', EditProfileView.as_view(), name='edit-profile'),
    path('password-change/', ChangePasswordView.as_view(), name='password-change'),
    path('password-change/done/', PasswordChangeDoneView.as_view(template_name='accounts/password_change_done.html'), name='password_change_done'),
    path('password-reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/confirm/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]
