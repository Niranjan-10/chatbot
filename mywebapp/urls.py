
from django.urls import path
from . import views

urlpatterns = [
    path('',views.home),
    path('webhook',views.getinfo),
    path('test', views.test)

]