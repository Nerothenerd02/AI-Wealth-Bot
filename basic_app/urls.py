from django.contrib import admin
from django.urls import path
from basic_app import views

app_name = 'basic_app'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('home/', views.index, name='index'),
    path('login/', views.loginPage, name='login'),
    path('logout/', views.logoutUser, name='logout'),
    path('register/', views.registerPage, name='register'),
    path('profile/', views.profile, name='profile'),
    path('stats/', views.statisticsAdmin, name='stats'),

    path('search/', views.search_stock, name='search_stock'),  # <<<<<< HERE

    path('admin/', admin.site.urls),
    path('emotion', views.emotion_view, name='emotion'),

    path('home/<str:symbol>', views.stock, name='stock'),
    path('home/<str:symbol>/price_prediction', views.price_prediction, name='prediction'),
    path('home/<str:symbol>/add', views.addToPortfolio, name='addToPortfolio'),

    path('portfolio/', views.portfolio, name='portfolio'),
    path('portfolio/<str:symbol>/remove', views.removeFromPortfolio, name='removeFromPortfolio'),
    path('portfolio/<str:symbol>/quantityAdd', views.quantityAdd, name='quantityAdd'),
    path('portfolio/<str:symbol>/quantitySub', views.quantitySub, name='quantitySub'),
    path('portfolio/add_cash/', views.add_cash, name='add_cash'),
    path('portfolio/withdraw_cash/', views.withdraw_cash, name='withdraw_cash'),

    path('explore/', views.explore_stocks, name='explore_stocks'),
    path('indicator/<str:symbol>/<str:indicator>/', views.get_indicator, name='get_indicator'),

]
