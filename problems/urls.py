from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("applications/", views.applications_list, name="applications_list"),
    path("applications/new/", views.create_application, name="create_application"),
    path("categories/new/", views.create_application_category, name="create_application_category"),
    path("applications/<int:application_id>/edit/", views.edit_application, name="edit_application"),
    path("applications/<int:application_id>/assign/", views.attach_performer, name="attach_performer"),
    path("applications/<int:application_id>/", views.application_detail, name="application_detail"),
    path("profile/", views.profile, name="profile"),
]
