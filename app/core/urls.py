
from django.urls import path
from .views import IndexView,PredictView

urlpatterns=[
    path('', IndexView,name='home'),
    path('<str:pk>/',PredictView, name='league'),
]