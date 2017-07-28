import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as numpy
import pickle
import argparse

from matplotlib.widgets import Button

# colour of matplotlib buttons
color = 'lightgoldenrodyellow'
# color of matplotlib buttons when mouse is over them
hovercolor = '0.975'

def loadimages(path):
	""" Function to explore a a directory and sub-directories, adding each file path it finds to an array """
	# input: filepath for top directory.
	import os.path
	from os import walk

	f = []
	for (dirpath, dirnames, filenames) in walk(path):
		for file in filenames:
			f.append(os.path.join(dirpath,file))
	return f

def loadcoordinates(file):
	""" Function to load a multidimensional array of coordinate pairs from a pickle file. """
	# input: pkl file.
	# note: if pkl file doesn't exist, a blank one is made.
	c = {}
	try:
		with open(file) as f:
			c = pickle.load(f)
	except IOError:
		with open(file, "w") as f:
			pickle.dump(c,f)
	return c

def drawboxfromcoords(coords):
	""" Function to draw a bounding box with an arbritrary number of coordinate points in an image. """
	# input: array of x,y coordinate pairs.
	global fig

	for i in range(0,len(coords)):
		# plot lines between all coordinate pairs, linking the last pair to the first.
		line, = ax.plot((coords[i][0], coords[(i+1) % (len(coords))][0]), (coords[i][1], coords[(i+1) % (len(coords))][1]))
		fig.canvas.draw()
	# since we are drawing a complete box already, disable mouse input.
	fig.canvas.mpl_disconnect(cid)

def click(event):
	""" Function to record the x,y location of any mouse click that happens inside a plotted image. """
	""" When more than 1 locations have been recorded, lines will be drawn to connect these. """
	global coords

	x,y = event.xdata, event.ydata
	# if we click outside of the image, don't record coordinates.
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
	""" Function to save the current bounding box coordinates to a dictionary. """
	global coords, all_coords, fig

	# Get image details.
	img_name = images[imgindex].split("/")[-1]
	classification = images[imgindex].split("/")[1]

	all_coords[img_name] = []
	all_coords[img_name].append(classification)
	all_coords[img_name].extend(coords)


	coords = []

	# redraw the image and the connected set of coordinates.
	ax.cla()
	
	# Get image details.
	img_name = images[imgindex].split("/")[-1]
	classification = images[imgindex].split("/")[1]

	img = mpimg.imread(images[imgindex])
	ax.imshow(img)
	ax.set_title(classification + " : " + img_name)
	print(all_coords[img_name])
	if img_name in all_coords:
		drawboxfromcoords(all_coords[img_name][1:])
	fig.canvas.draw()
	# disable drawing of new coordinates.
	fig.canvas.mpl_disconnect(cid)

def saveandclose(event):
	""" Function to save the dictionary of all coordinate sets for each image to the specified pickle file. """
	global all_coords, coordinatesfile

	with open(coordinatesfile, 'w') as f:
		pickle.dump(all_coords,f)

	# disable mouse input and close the plot.
	fig.canvas.mpl_disconnect(cid)
	plt.close()	# note this actually terminates the program.

def nextimage(event):
	""" Function to discard currently recorded coordinates and graph the next image in the list of images. """
	global images, imgindex, coords, all_coords, cid
	# if we are at the last image, don't do anything.
	if imgindex == (len(images) - 1):
		return
	imgindex += 1
	coords = []
	# redraw the figure with the new image.
	ax.cla()

	# Get image details.
	img_name = images[imgindex].split("/")[-1]
	classification = images[imgindex].split("/")[1]
	img = mpimg.imread(images[imgindex])
	ax.imshow(img)
	ax.set_title(classification + " : " + img_name)

	# if we already have a set of coordinates saved, draw the box. Otherwise, enable mouse input. """
	if img_name in all_coords:
		if len(all_coords[img_name]) == 0:
			cid = fig.canvas.mpl_connect('button_press_event', click)
		else:
			drawboxfromcoords(all_coords[img_name][1:])
			fig.canvas.mpl_disconnect(cid)
	else:
		cid = fig.canvas.mpl_connect('button_press_event', click)
	fig.canvas.draw()

def previmage(event):
	""" Function to discard currently recorded coordinates and graph the previous image in the list of images. """
	global images, imgindex, coords, all_coords, cid
	# if we are at the first image, don't do anything.
	if imgindex == 0:
		return
	imgindex -= 1
	coords = []
	# redraw the figure with the new image.
	ax.cla()

	# Get image details.
	img_name = images[imgindex].split("/")[-1]
	classification = images[imgindex].split("/")[1]
	img = mpimg.imread(images[imgindex])
	ax.imshow(img)
	ax.set_title(classification + " : " + img_name)

	# if we already have a set of coordinates saved, draw the box. Otherwise, enable mouse input. """
	if img_name in all_coords:
		if len(all_coords[img_name]) == 0:
			cid = fig.canvas.mpl_connect('button_press_event', click)
		else:
			drawboxfromcoords(all_coords[img_name][1:])
			fig.canvas.mpl_disconnect(cid)
	else:
		cid = fig.canvas.mpl_connect('button_press_event', click)
	fig.canvas.draw()

def reset(event):
	""" Function that discards the currently recorded coordinates and removes any drawn lines from the image. """
	global coords, fig, ax

	coords = []
	# enable mouse input, we have cleared the previous coordinates so we need to make new ones.
	cid = fig.canvas.mpl_connect('button_press_event', click)
	# redraw the figure with just the new image.
	ax.cla()
	img = mpimg.imread(images[imgindex])
	ax.imshow(img)
	ax.set_title(images[imgindex])
	fig.canvas.draw()

def joinstartend(event):
	""" Function that connects the last recorded coordinate to the first recorded one, closing the bounding box. """
	# Note: this is purely for visual effects, does not modify what coordinates are stored.
	global coords, fig, ax

	if len(coords) < 2:
		return
	coord1 = coords[0]
	coord2 = coords[len(coords)-1]
	line, = ax.plot((coord1[0],coord2[0]),(coord1[1],coord2[1]),'k-')
	fig.canvas.draw()

def dictContains(dict, img_name):
	""" Function to check whether a image (by image name) is currently in the dictionary. """
	# Note: need to iterate over the dictionary here, since each value is a [image_name,coords] collection. 
	for key,value in dict.iteritems():
		if value[0] == img_name:
			return True
	return False


if __name__ == '__main__':
	# Command line argument setup. Set program defaults from the supplied arguments. 
	parser = argparse.ArgumentParser(description='')
	parser.add_argument('image_directory', default='images', type=str, help="")
	parser.add_argument('coordinates_file', default='coordinates.pkl', type=str, help="")
	args = parser.parse_args()
	coordinatesfile = args.coordinates_file
	imagedir = args.image_directory

	# Initialize the figure and axes we will be drawing images and lines on.
	fig = plt.figure()
	ax = fig.add_subplot(111)

	""" The following lines of code are setting up each button in the UI to correspond to the appropriate function handlers above. """
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
	""" End setting up button code. """

	# Enable mouse input for recording coordinates.
	cid = fig.canvas.mpl_connect('button_press_event', click)

	# Initialize program defaults, load the set of images and pre-saved coordinates (if any).
	imgindex = 0
	images = loadimages(imagedir)
	# Convert image name to unix path format.
	for i in range(0,len(images)):
		images[i] = images[i].replace("\\","/")
	
	coords = []
	all_coords = loadcoordinates(coordinatesfile)

	# Get image details.
	img_name = images[imgindex].split("/")[-1]
	classification = images[imgindex].split("/")[1]

	# Plot the first image and it's bounding box (if saved previously)
	img = mpimg.imread(images[imgindex])
	ax.imshow(img)
	ax.set_title(classification + " : " + img_name)

	# Display image bounding box if it already exists.
	if img_name in all_coords:
		if len(all_coords[img_name]) == 0:
			cid = fig.canvas.mpl_connect('button_press_event', click)
		else:
			drawboxfromcoords(all_coords[img_name][1:])
			fig.canvas.mpl_disconnect(cid)

	# Finally, show the plot.
	plt.show()
