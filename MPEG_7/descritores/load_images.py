import EHD
from PIL import Image
import os
from models import ImageModel
import json

images_dir = "Image_Dataset/"

for filename in os.listdir(images_dir):
    if os.path.isfile(os.path.join(images_dir, filename)):

        print(filename)

        img = Image.open(images_dir + filename)
        edh = EHD.EHD_Descriptor(0.1)
        ehd_img = edh.Apply(img)
        ehd_img = json.dumps(ehd_img)

        image = ImageModel(name=filename, image=img, edge_histogram=ehd_img, color_layout="A")
        image.save()
