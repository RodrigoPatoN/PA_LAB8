from django.urls import path
from .views import select_image, get_similar, insert_images


urlpatterns = [
    path('select-image', select_image, name='select-image'),
    path("similar/", get_similar, name="get-similar"),
    #path("insert-images/", insert_images, name="insert-images")
]
