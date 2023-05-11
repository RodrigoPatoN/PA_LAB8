from django.shortcuts import render, redirect
from .forms import InsertImage
import os
import json
from .EHD import EHD_Descriptor
from .CLD import CLD_Descriptor
from PIL import Image
from .models import ImageModel
import numpy as np
from MPEG_7.settings import BASE_DIR, MEDIA_URL
from django.core.files.storage import default_storage
from .t2 import CLD_Descriptor as CLD_Descriptor2
import math


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
        
        image = Image.open(im)
        cld = CLD_Descriptor2()
        cld.apply(image)

        desc_y = cld.YCoeff
        desc_cb = cld.CbCoeff
        desc_cr = cld.CrCoeff

        distances = []

        for img in ImageModel.objects.all():

            img_desc_y = eval(img.color_layout_y)
            img_desc_y = np.array(img_desc_y)

            img_desc_cb = eval(img.color_layout_cb)
            img_desc_cb = np.array(img_desc_cb)

            img_desc_cr = eval(img.color_layout_cr)
            img_desc_cr = np.array(img_desc_cr)

            dist = get_dist_cld(desc_y, img_desc_y, desc_cb, img_desc_cb, desc_cr, img_desc_cr)
            distances.append([img.pk, dist])
        
        sorted_list = sorted(distances, key=lambda x: x[1])
        closest = sorted_list[:int(num)]
        print(closest)

        for img_close in closest:
            images_return.append(ImageModel.objects.get(pk=img_close[0]))
        
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

    i = 0

    for filename in os.listdir(images_dir):
        print(i)
        i += 1
        if os.path.isfile(os.path.join(images_dir, filename)):

            print(filename)

            img_path = images_dir + filename

            img = Image.open(img_path)
            edh = EHD_Descriptor(0.1)
            ehd_img = edh.Apply(img)
            ehd_img = json.dumps(ehd_img.tolist())

            cld = CLD_Descriptor2()
            cld.apply(img)

            cld_y = cld.YCoeff
            cld_cb = cld.CbCoeff
            cld_cr = cld.CrCoeff

            cld_y = json.dumps(cld_y.tolist())
            cld_cb = json.dumps(cld_cb.tolist())
            cld_cr = json.dumps(cld_cr.tolist())

            image = ImageModel(name=filename, image="/static/images/" + filename, edge_histogram=ehd_img, color_layout_y=cld_y, color_layout_cb=cld_cb, color_layout_cr=cld_cr)
            image.save()

    return render(request, 'images_inserted.html', {})


def get_dist_ehd(desc1, desc2):

    dist = 0

    global_1 = []
    global_2 = []

    for i in range(5):
        g1 = desc1[i::5]
        g2 = desc2[i::5]

        global_1.append(sum(g1))
        global_2.append(sum(g2))

    for i in range(5):
        dist += abs(global_1[i] - global_2[i])

    for i in range(80):
        dist += abs(desc1[i] - desc2[i])

    return dist

def get_dist_cld(desc1y, desc2y, desc1cb, desc2cb, desc1cr, desc2cr):

    zigzag = [0, 1, 8, 16, 9, 2, 3, 10, 17, 24, 32, 25, 18, 11, 4, 5,
        12, 19, 26, 33, 40, 48, 41, 34, 27, 20, 13, 6, 7, 14, 21, 28,
        35, 42, 49, 56, 57, 50, 43, 36, 29, 22, 15, 23, 30, 37, 44, 51,
        58, 59, 52, 45, 38, 31, 39, 46, 53, 60, 61, 54, 47, 55, 62, 63]

    dist_y = 0
    dist_cb = 0
    dist_cr = 0

    for i in zigzag:
        
        dist_y += (desc1y[i] - desc2y[i])**2
        dist_cb += (desc1cb[i] - desc2cb[i])**2
        dist_cr += (desc1cr[i] - desc2cr[i])**2

    dist = math.sqrt(dist_y) + math.sqrt(dist_cb) + math.sqrt(dist_cr)

    return dist