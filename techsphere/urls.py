from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/register/', include(('main.urls', 'main'), namespace='main_register')), # Unique namespace for registration URLs
    path('', include(('main.urls', 'main'), namespace='main')), # Keep this for other main app URLs
]