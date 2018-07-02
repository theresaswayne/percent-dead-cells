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
	print "The full path is " + str(inputPath)
	
	fileWithExt = os.path.basename(inputPath)
	print "The filename is " + str(fileWithExt)

	fileName = os.path.splitext(fileWithExt)[0]
	print "The file name without extension is " + str(fileName) 
	
	baseName = fileName.split("Scene") # should yield 2 components. 2nd contains scene, pos, well
	print "The base image name is " + str(baseName[0])

	posInfo = splitName[1].split("-") # hyphens
	
	# basename = splitName[0] # first component
	# posInfo = splitName[1] # second component
	# posName = posInfo.split("-")
	# format -XXX-PX[X]-RC[C].ext

	#well = posInfo[3]
	#pos = posInfo[2]

	# DUMMY VALUES FOR TESTING
	basename = "b"
	well = "w"
	pos = "p"
	
	result = (basename, well, pos) # string tuple
	return result


imageInfo = parse_path(inputImage)
baseName = imageInfo[0]
wellName = imageInfo[1]
posName = imageInfo[2]
print "This is image " + baseName + ", well " +wellName+", position "+posName