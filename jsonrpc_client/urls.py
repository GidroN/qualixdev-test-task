from django.urls import path

from .views import InputFormView

urlpatterns = [
    path('', InputFormView.as_view(), name='main')
]
