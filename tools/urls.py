from django.urls import path
from .views import compress_view,resize_view,convert_view,batch_view,thumbnail_view, crop_view, enhance_view, filter_view

urlpatterns = [
    path('compress/', compress_view, name='compress'),
    path('resize/', resize_view, name='resize'),
    path('convert/', convert_view, name='convert'),
    path('batch/', batch_view, name='batch'),
    path('thumbnail/', thumbnail_view, name='thumbnail'),
    path('crop/', crop_view, name='crop'),
    path('enhance/', enhance_view, name='enhance'),
    path('filter/', filter_view, name='filter'),
]