from CLD import CLD_Descriptor
from PIL import Image
from t2 import CLD_Descriptor as CLD_Descriptor2

image = Image.open("./Image_Dataset/300493d-alien-magic-matrix-screen-saver-is-reloaded-by-power-of-neo-and-trinity.jpg")

cld = CLD_Descriptor()
image_description = cld.Apply(image)

cl2 = CLD_Descriptor2()
image_description2 = cl2.apply(image)

print(cld.YCoeff)
print(cld.CbCoeff)
print(cld.CrCoeff)

print(cl2.YCoeff)
print(cl2.CbCoeff)
print(cl2.CrCoeff)