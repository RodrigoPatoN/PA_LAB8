from django.shortcuts import render, redirect
from .forms import InsertImage
import os
import json
from .EHD import EHD_Descriptor
from PIL import Image
from .models import ImageModel, ImageInserted
import numpy as np
from MPEG_7.settings import BASE_DIR, MEDIA_URL
from django.core.files.storage import default_storage


# Create your views here.

def select_image(request):
    form = InsertImage
    return render(request, 'select_image.html', {'form':form,})


def get_similar(request):

    num = request.POST.get('num_images')
    descriptor = request.POST.get('descriptor')
    im = request.FILES.get('image')

    filename = default_storage.save('images/inserted_' + im.name, im)

    image_path = f"../{MEDIA_URL}{filename}"
    print(image_path)

    images_return = []

    if descriptor == "Color Layout":
        print("Color Layout")
        
    elif descriptor == "Edge Histogram":

        image = Image.open(im)
        ehd = EHD_Descriptor(1)
        image_description = ehd.Apply(image)

        distances = []

        for img in ImageModel.objects.all():
            img_desc = eval(img.edge_histogram)

            img_desc = np.array(img_desc)

            dist = get_dist_ehd(image_description, img_desc)

            distances.append([img.pk, dist])
        
        sorted_list = sorted(distances, key=lambda x: x[1])
        closest = sorted_list[:int(num)]
        print(closest)

        for img_close in closest:
            images_return.append(ImageModel.objects.get(pk=img_close[0]))

    else:
        print("Error")
        print(descriptor)
        return redirect("select-image")
    

    return render(request, 'get_similar.html', {"images": images_return, "image_inserted": image_path, "descriptor": descriptor, "num_images": num})


def insert_images(request):

    images_dir = str(BASE_DIR) + "/descritores/static/images/"
    print(images_dir)

    for filename in os.listdir(images_dir):
        if os.path.isfile(os.path.join(images_dir, filename)):

            img_path = images_dir + filename

            img = Image.open(img_path)
            edh = EHD_Descriptor(0.1)
            ehd_img = edh.Apply(img)
            ehd_img = json.dumps(ehd_img.tolist())

            image = ImageModel(name=filename, image="/static/images/" + filename, edge_histogram=ehd_img, color_layout="A")
            image.save()

    return render(request, 'images_inserted.html', {})


def get_dist_ehd(desc1, desc2):

    dist = 0

    for i in range(80):
        dist += abs(desc1[i] - desc2[i])

    return dist