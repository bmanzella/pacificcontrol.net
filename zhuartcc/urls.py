from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from apps.event import views as event
from apps.resource import views as resource
from apps.training import views as training
from apps.uls import views as uls
from apps.user import views as user
from apps.views import views as views
from apps.visit import views as visit

urlpatterns = [
    # Event
    path('events/', event.view_all_events),                             # View All Events
    path('events/<int:id>', event.view_event),                          # View Event
    path('events/<int:id>/edit', event.edit_event),                     # Edit Event (STAFF)
    path('events/new', event.create_event),                             # Create Event (STAFF)

    # Resource
    path('resources/', resource.view_resources),                        # View Resources
    path('resources/add/', resource.add_resource),                      # Add Resource (POST / STAFF)
    path('resources/edit/', resource.edit_resource),                    # Edit Resource (POST / STAFF)
    path('resources/delete/', resource.delete_resource),                # Delete Resource (POST / STAFF)

    # Training
    path('training/', training.view_training_center),                   # View Training Center Home
    path('training/schedule/', training.schedule),                      # View Session Details
    path('training/history/<int:cid>/', training.view_history),         # View Session Details

    # ULS (Auth)
    path('login/', uls.login),                                          # Login via VATUSA ULS
    path('logout/', uls.logout),                                        # Logout + Delete Session Data

    # User
    path('staff/', user.view_staff),                                    # View Staff
    path('roster/', user.view_roster),                                  # View Roster
    path('roster/<int:cid>/', user.view_user_profile),                  # View User Profile
    path('roster/<int:cid>/edit/', user.edit_user),                     # Edit User (STAFF)

    # Views
    path('', views.view_homepage),                                      # View Homepage
    path('privacy/', views.view_privacy_policy),                        # View Privacy Policy

    # Visit
    path('visit/', visit.submit_visiting_request),                      # Submit Visiting Request
    path('requests/', visit.view_visiting_requests),                    # View All Visiting Requests

    path('django/', admin.site.urls),                                   # django Admin Panel
]

# Allows access of media files such as documents and user profiles
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)