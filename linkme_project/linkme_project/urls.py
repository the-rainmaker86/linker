from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('linkme.urls')),  # Assumes your movies app has its own urls.py.
]