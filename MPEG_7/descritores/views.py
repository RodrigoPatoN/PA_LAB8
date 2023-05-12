from django.shortcuts import render, redirect
from .forms import InsertImage
import os
import json
from .EHD import EHD_Descriptor
from .CLD import CLD_Descriptor as CLD_Descriptor
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

    try:

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
    
    except:
        return redirect('select-image')


def insert_images(request):

    images_dir = str(BASE_DIR) + "/descritores/static/images/"

    for filename in os.listdir(images_dir):

        if os.path.isfile(os.path.join(images_dir, filename)):

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

    verticals1 = []
    horizontals1 = []
    squares1 = []

    verticals2 = []
    horizontals2 = []
    squares2 = []

    for i in range(5):

        g1 = desc1[i::5]
        g2 = desc2[i::5]

        global_1.append(sum(g1))
        global_2.append(sum(g2))

    for i in range(4):

        h1_1 = desc1[i*20:i*20+5]
        h1_2 = desc1[i*20+5:i*20+10]
        h1_3 = desc1[i*20+10:i*20+15]
        h1_4 = desc1[i*20+15:(i+1)*20]

        h2_1 = desc2[i*20:i*20+5]
        h2_2 = desc2[i*20+5:i*20+10]
        h2_3 = desc2[i*20+10:i*20+15]
        h2_4 = desc2[i*20+15:(i+1)*20]

        v1_1 = desc1[i*5:i*5+5]
        v1_2 = desc1[i*5+20:i*5+25]
        v1_3 = desc1[i*5+40:i*5+45]
        v1_4 = desc1[i*5+60:i*5+65]

        v2_1 = desc2[i*5:i*5+5]
        v2_2 = desc2[i*5+20:i*5+25]
        v2_3 = desc2[i*5+40:i*5+45]
        v2_4 = desc2[i*5+60:i*5+65]

        h1 = [sum(lst) / len(lst) for lst in zip(*[h1_1, h1_2, h1_3, h1_4])]
        h2 = [sum(lst) / len(lst) for lst in zip(*[h2_1, h2_2, h2_3, h2_4])]

        v1 = [sum(lst) / len(lst) for lst in zip(*[v1_1, v1_2, v1_3, v1_4])]
        v2 = [sum(lst) / len(lst) for lst in zip(*[v2_1, v2_2, v2_3, v2_4])]

        horizontals1.extend(h1)
        horizontals2.extend(h2)
        
        verticals1.extend(v1)
        verticals2.extend(v2)


    for i in range(5):

        if i == 0:

            sq1_1 = desc1[0:5]
            sq1_2 = desc1[5:10]
            sq1_3 = desc1[20:25]
            sq1_4 = desc1[25:30]

            sq2_1 = desc2[0:5]
            sq2_2 = desc2[5:10]
            sq2_3 = desc2[20:25]
            sq2_4 = desc2[25:30]

        elif i == 1:

            sq1_1 = desc1[10:15]
            sq1_2 = desc1[15:20]
            sq1_3 = desc1[30:35]
            sq1_4 = desc1[35:40]

            sq2_1 = desc2[10:15]
            sq2_2 = desc2[15:20]
            sq2_3 = desc2[30:35]
            sq2_4 = desc2[35:40]
        
        elif i == 2:

            sq1_1 = desc1[40:45]
            sq1_2 = desc1[45:50]
            sq1_3 = desc1[60:65]
            sq1_4 = desc1[65:70]

            sq2_1 = desc2[40:45]
            sq2_2 = desc2[45:50]
            sq2_3 = desc2[60:65]
            sq2_4 = desc2[65:70]

        elif i == 3:

            sq1_1 = desc1[50:55]
            sq1_2 = desc1[55:60]
            sq1_3 = desc1[70:75]
            sq1_4 = desc1[75:80]

            sq2_1 = desc2[50:55]
            sq2_2 = desc2[55:60]
            sq2_3 = desc2[70:75]
            sq2_4 = desc2[75:80]
        
        else:

            sq1_1 = desc1[25:30]
            sq1_2 = desc1[30:35]
            sq1_3 = desc1[45:50]
            sq1_4 = desc1[50:55]

            sq2_1 = desc2[25:30]
            sq2_2 = desc2[30:35]
            sq2_3 = desc2[45:50]
            sq2_4 = desc2[50:55]

        s1 = [sum(lst) / len(lst) for lst in zip(*[sq1_1, sq1_2, sq1_3, sq1_4])]
        s2 = [sum(lst) / len(lst) for lst in zip(*[sq2_1, sq2_2, sq2_3, sq2_4])]

        squares1.extend(s1)
        squares2.extend(s2)
    
    semi_global1 = horizontals1 + verticals1 + squares1
    semi_global2 = horizontals2 + verticals2 + squares2

    for i in range(80):
        dist += abs(desc1[i] - desc2[i])

    for i in range(5):
        dist += 5 * abs(global_1[i] - global_2[i])

    for i in range(65):
        dist += abs(semi_global1[i] - semi_global2[i])

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