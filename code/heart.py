import numpy as numpy
import scipy as scipy
import matplotlib as mplot
from matplotlib import pylab
from pylab import *
import seaborn as sns
import PIL
from PIL import Image
import os


x = scipy.linspace(-2,2,1000)
y1 = scipy.sqrt(1-(abs(x)-1)**2) #scipy.sqrt(1-(abs(x)-1)**2)
y2 = -3*scipy.sqrt(1-(abs(x)/2)**0.5) #-3*scipy.sqrt(1-(abs(x)/2)**0.5)

fig = plt.figure(figsize=(6,4))
ax = fig.add_subplot(1, 1, 1)
ax.set_facecolor('black')
sns.set_style("dark", {"axes.facecolor":"black", "axes.grid":False, "text.color":"black", "xtick.color":"black", "ytick.color":"black"})
pylab.fill_between(x, y1, color='white')
pylab.fill_between(x, y2, color='white')
ax.axes.get_xaxis().set_visible(False)
ax.axes.get_yaxis().set_visible(False)
pylab.savefig('heart.jpg', bbox_inches='tight', pad_inches=-0.1)

imageFile = 'heart.jpg'
image_obj = Image.open(imageFile)
width = 360
height = 240
image_resize = image_obj.resize((width,height), Image.ANTIALIAS)
image_resize.save("heart.jpg")

#path = photos/love_photo_%s.jpg
i = 0
#while os.path.exists("/home/coolperson/Desktop/love_%s.jpeg" % i):
for i in range(1,4):
	#printImage.save("photos/love_photo_%s.jpg" % i)

	imageFile = '/home/coolperson/Desktop/love_%s.jpeg' %i
	image_obj = Image.open(imageFile)
	width = 360
	height = 240
	
	background = image_resize = image_obj.resize((width,height), Image.ANTIALIAS)
	overlay = Image.open("heart.jpg")

	background = background.convert("RGBA")
	overlay = overlay.convert("RGBA")

	new_img = Image.blend(background, overlay, 0.5)
	new_img.save("lover_%s.png" %i,"PNG")