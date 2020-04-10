from django.urls import path

from . import views

app_name = 'polls'
urlpatterns = [
    # ex: /polls/
    path('', views.index, name='index'),
    # ex: /polls/logout/
    path('logout_view/', views.logout_view, name='logout_view'),
    #path('q2/', views.q2, name='q2'),
    #path('q3/', views.q3, name='q3'),
    path('login_view/', views.login_view, name='login_view'),
    path('register/', views.register, name='register'),
]