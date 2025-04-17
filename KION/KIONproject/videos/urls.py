from django.contrib import admin
from django.urls import path
from .views import view_event_page

urlpatterns = [
    path('view_event/', view_event_page, name='view_event'),
]
