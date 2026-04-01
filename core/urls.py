"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from inventory.views import sales_dashboard, add_to_cart, clear_cart, checkout
from inventory.views import initiate_stk_push, mpesa_callback

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', sales_dashboard, name='dashboard'), # Your main POS screen
    path('add/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('clear/', clear_cart, name='clear_cart'),
    path('checkout/', checkout, name='checkout'),
    path('payment/stk-push/', initiate_stk_push, name='initiate_stk_push'),
    path('mpesa/callback/', mpesa_callback, name='mpesa_callback'),
]
