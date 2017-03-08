import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as numpy
import pickle
import argparse

from matplotlib.widgets import Button

color = 'lightgoldenrodyellow'
hovercolor = '0.975'


imagedir = ''

images = []
imgindex = None


coordinatesfile = ''

coords = []
all_coords = {}

def loadimages(path):
	import os.path
	from os import walk

	f = []
	for (dirpath, dirnames, filenames) in walk(path):
		for file in filenames:
			f.append(os.path.join(dirpath,file))
	return f

def loadcoordinates(file):
	c = {}
	try:
		with open(file) as f:
			c = pickle.load(f)
	except IOError:
		with open(file, "w") as f:
			pickle.dump(c,f)
	return c

def drawboxfromcoords(coords):
	global fig

	for i in range(0,len(coords)):
		line, = ax.plot((coords[i][0], coords[(i+1) % (len(coords))][0]), (coords[i][1], coords[(i+1) % (len(coords))][1]))
		fig.canvas.draw()
	fig.canvas.mpl_disconnect(cid)

def click(event):
	global coords

	x,y = event.xdata, event.ydata
	if x == None or y == None:
		return
	if x <= 1 or y <= 1:
		return
	coords.append((int(x),int(y)))
	if len(coords) > 1:
		coord1 = coords[len(coords)-1]
		coord2 = coords[len(coords)-2]
		line, = ax.plot((coord1[0],coord2[0]),(coord1[1],coord2[1]),'k-')
		fig.canvas.draw()
	elif len(coords) == 1:
		line, = ax.plot(coords[0][0],coords[0][1], 'or')
		fig.canvas.draw()

def save(event):
	global coords, all_coords, fig

	all_coords[images[imgindex]] = coords
	coords = []
	ax.cla()
	img = mpimg.imread(images[imgindex])
	ax.imshow(img)
	ax.set_title(images[imgindex])
	if images[imgindex] in all_coords:
		drawboxfromcoords(all_coords[images[imgindex]])
	fig.canvas.draw()
	fig.canvas.mpl_disconnect(cid)

def saveandclose(event):
	global all_coords, coordinatesfile

	with open(coordinatesfile, 'w') as f:
		pickle.dump(all_coords,f)

	fig.canvas.mpl_disconnect(cid)
	plt.close()

def nextimage(event):
	global images, imgindex, coords, all_coords, cid

	if imgindex == (len(images) - 1):
		return
	imgindex += 1
	coords = []
	ax.cla()
	img = mpimg.imread(images[imgindex])
	ax.imshow(img)
	ax.set_title(images[imgindex])
	if images[imgindex] in all_coords:
		if len(all_coords[images[imgindex]]) == 0:
			cid = fig.canvas.mpl_connect('button_press_event', click)
		else:
			drawboxfromcoords(all_coords[images[imgindex]])
			fig.canvas.mpl_disconnect(cid)
	else:
		cid = fig.canvas.mpl_connect('button_press_event', click)
	fig.canvas.draw()

def previmage(event):
	global images, imgindex, coords, all_coords, cid

	if imgindex == 0:
		return
	imgindex -= 1
	coords = []
	ax.cla()
	img = mpimg.imread(images[imgindex])
	ax.imshow(img)
	ax.set_title(images[imgindex])
	if images[imgindex] in all_coords:
		if len(all_coords[images[imgindex]]) == 0:
			cid = fig.canvas.mpl_connect('button_press_event', click)
		else:
			drawboxfromcoords(all_coords[images[imgindex]])
			fig.canvas.mpl_disconnect(cid)
	else:
		cid = fig.canvas.mpl_connect('button_press_event', click)
	fig.canvas.draw()

def reset(event):
	global coords, fig, ax

	coords = []
	cid = fig.canvas.mpl_connect('button_press_event', click)
	ax.cla()
	img = mpimg.imread(images[imgindex])
	ax.imshow(img)
	ax.set_title(images[imgindex])
	fig.canvas.draw()

def joinstartend(event):
	global coords, fig, ax

	if len(coords) < 2:
		return
	coord1 = coords[0]
	coord2 = coords[len(coords)-1]
	line, = ax.plot((coord1[0],coord2[0]),(coord1[1],coord2[1]),'k-')
	fig.canvas.draw()

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='')
	parser.add_argument(
		'image_directory',
		default='images',
		type=str,
		help="")
	parser.add_argument(
		'coordinates_file',
		default='coordinates.pkl',
		type=str,
		help="")
	args = parser.parse_args()
	coordinatesfile = args.coordinates_file
	imagedir = args.image_directory

	fig = plt.figure()
	ax = fig.add_subplot(111)

	save_b_ax = fig.add_axes([0.8,0.05,0.1,0.04])
	save_b = Button(save_b_ax,'Save',color=color,hovercolor=hovercolor)
	save_b.on_clicked(save)

	saveandclose_b_ax = fig.add_axes([0.125,0.05,0.2,0.04])
	saveandclose_b = Button(saveandclose_b_ax,'Save all and close',color=color,hovercolor=hovercolor)
	saveandclose_b.on_clicked(saveandclose)

	next_b_ax = fig.add_axes([0.8,0.925,0.1,0.04])
	next_b = Button(next_b_ax,'Next',color=color,hovercolor=hovercolor)
	next_b.on_clicked(nextimage)

	prev_b_ax = fig.add_axes([0.125,0.925,0.1,0.04])
	prev_b = Button(prev_b_ax,'Prev',color=color,hovercolor=hovercolor)
	prev_b.on_clicked(previmage)

	reset_b_ax = fig.add_axes([0.65,0.05,0.1,0.04])
	reset_b = Button(reset_b_ax,'Reset',color=color,hovercolor=hovercolor)
	reset_b.on_clicked(reset)

	joinstartend_b_ax = fig.add_axes([0.4,0.05,0.2,0.04])
	joinstartend_b = Button(joinstartend_b_ax,'Join end to start',color=color,hovercolor=hovercolor)
	joinstartend_b.on_clicked(joinstartend)

	cid = fig.canvas.mpl_connect('button_press_event', click)

	imgindex = 0
	images = loadimages(imagedir)
	all_coords = loadcoordinates(coordinatesfile)
	img = mpimg.imread(images[imgindex])
	ax.imshow(img)
	ax.set_title(images[imgindex])
	if images[imgindex] in all_coords:
		if len(all_coords[images[imgindex]]) == 0:
			cid = fig.canvas.mpl_connect('button_press_event', click)
		else:
			drawboxfromcoords(all_coords[images[imgindex]])
			fig.canvas.mpl_disconnect(cid)
	plt.show()
