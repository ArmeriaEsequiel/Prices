"""trydjango URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from pages import views
from product.views import *
from django.contrib.auth import views as auth_views

urlpatterns = [
	path('', views.home_view, name='home_view'),
	path('search/', views.search_view, name= 'search_view'),
	path('price/', price_view, name ='price_view'),
	path('load/', load_base_view, name ='load_base_view'),
	path('modify/', modify_product_view, name ='modify_product_view'),
    path('delete/', delete_single_price_view, name ='delete_single_price'),
    path('update_single/', update_single_price_view, name ='update_single_price'),
    path('update/<int:position_id>/', update_price_view, name ='update'),
    path('from_file/', modify_price_from_file_view, name ='modify_from_file_view'),
    path('admin/', admin.site.urls),
    path('', include("django.contrib.auth.urls")),
    #path('', auth_views.LoginView ,{'template_name' : 'core/login.html'}, name='login'),
]
