from django.contrib import admin
from django.urls import path ,include
from . import views

urlpatterns = [
    path('', views.register, name="register"),
    path('stockpicker', views.stockPicker ,name='stockpicker'),
    path('stocktracker/', views.stockTracker ,name='stocktracker'),
    
    path("login/", views.login, name="login"),
    
    path("get_stock_updates/", views.get_stock_updates, name="get_stock_updates")
    

]

