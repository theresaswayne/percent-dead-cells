#@File(label = "Input file") inputImage

# test function for splitting
import os
import sys
from ij import IJ


def parse_path(pathname):

	'''
	takes a filename object 
	returns a tuple of strings
	'''

	inputPath = pathname.getAbsolutePath() # this is needed and I'm not sure why
	#print "The full path is " + str(inputPath)
	
	fileWithExt = os.path.basename(inputPath)
	#print "The filename is " + str(fileWithExt)

	fileName = os.path.splitext(fileWithExt)[0]
	#print "The file name without extension is " + str(fileName) 
	
	base,info = fileName.split("Scene") # should yield 2 components. 2nd contains scene, pos, well
	base = base[:-1] # strip trailing hyphen
	#print "The base image name is " + str(base) 

	posInfo = info.split("-") # hyphens
	# format -scene-Ppos-well.ext
	
	scene = posInfo[1]
	pos = posInfo[2]
	well = posInfo[3]
	
	# DUMMY VALUES FOR TESTING
	#base = "b"
	#well = "w"
	#pos = "p"
	
	result = (base, well, pos) # string tuple
	return result


imageInfo = parse_path(inputImage)
baseName = imageInfo[0]
wellName = imageInfo[1]
posName = imageInfo[2]
print "This is image " + baseName + ", well " +wellName+", position "+posName