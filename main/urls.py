# main/urls.py #}
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'main'

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('create_team/', views.create_team, name='create_team'),
    path('create_team/<int:competition_id>/', views.create_team, name='create_team'),
    path('create_team/<int:competition_id>/<int:team_id>/', views.create_team, name='create_team'),
    path('check_team_name/', views.check_team_name, name='check_team_name'),
    path('competition/<int:pk>/', views.competition_detail, name='competition_detail'),
    path('register_competition/<int:pk>/', views.register_for_competition, name='register_for_competition'),
    path('payment_page/<int:competition_id>/', views.payment_page, name='payment_page'),
    path('payment_page/<int:competition_id>/<int:team_id>/', views.payment_page, name='payment_page'),
    path('message/<int:pk>/', views.message_page, name='message_page'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)