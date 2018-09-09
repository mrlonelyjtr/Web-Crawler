import tesserocr
from PIL import Image

image1 = Image.open('code1.jpg')
result1 = tesserocr.image_to_text(image1)
print(result1)

image2 = Image.open('code2.jpg') 
image2 = image2.convert('L') #转灰度
threshold = 110
table = []

for i in range(256):
    if i < threshold:
        table.append(0)
    else:
        table.append(1)

image2 = image2.point(table, '1') #二值化
#image2.show()
result2 = tesserocr.image_to_text(image2)
print(result2.replace(" ", ""))
