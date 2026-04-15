from django.urls import path

from . import views

app_name = 'orders'

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('', views.order_history, name='history'),
    path('<int:pk>/success/', views.order_success, name='success'),
    path('<int:pk>/cancel/', views.cancel_order, name='cancel'),
    path('<int:pk>/', views.order_detail, name='detail'),
]
