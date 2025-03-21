from django.urls import path
from .views import home, analyze_image, upload

urlpatterns = [
    path('', home, name='home'),
    path('upload/', upload, name ='upload'),
    path('analyze/', analyze_image, name='analyze'),
]
