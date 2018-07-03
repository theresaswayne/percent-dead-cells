#@File(label = "Input directory", style = "directory") inputDir
#@ String  (label = "File extension", value=".czi") ext


# test functions for splitting to get basename and well info from a directory in a single function

import os
import sys
from ij import IJ


def get_basename(dirName, ext):

	'''
	takes a directory (path) and an extension (string)
	returns a string: basename of the first file (in the directory) that matches the extension
	'''

	inputDir = dirName.getAbsolutePath() # this is needed and I'm not sure why

	for root, directories, filenames in os.walk(inputDir):
		filenames.sort()
		for filename in filenames:
			print "Checking:",filename
			# Check for file extension
			if not filename.endswith(ext):
				continue
	
			fileWithExt = os.path.basename(filename)
			#print "The filename is " + str(fileWithExt)

			fileName = os.path.splitext(fileWithExt)[0]
			#print "The file name without extension is " + str(fileName) 
	
			base = fileName.split("Scene")[0] # should yield 2 components. 2nd contains scene, pos, well
			base = base[:-1] # strip trailing hyphen
			#print "The base image name is " + base 

			return base # loop terminates after the first run


def parse_fileinfo(filename):

	'''
	takes a filename from a Zeiss multiwell exported file
	name format: basename-Scene-XXX-PX-WW.czi
	returns a tuple of strings:
		basename
		well number
		position number within the well
	'''

	fileWithExt = os.path.basename(filename)
	fileWithoutExt = os.path.splitext(fileWithExt)[0]
	#print "The filename is " + str(fileWithExt)
	#print "The file name without extension is " + str(fileWithoutExt) 

	base,info = fileWithoutExt.split("Scene") # should yield 2 components. 2nd contains scene, pos, well
	base = base[:-1] # strip trailing hyphen
	#print "The base image name is " + str(base) 

	posInfo = info.split("-")
	# format -scene-pos-well.ext ... first item in list is empty

	scene = posInfo[1] # not returned
	pos = posInfo[2]
	well = posInfo[3]
	
	result = (base, well, pos) # string tuple
	return result

# test harvesting basename from a file
firstBaseName = get_basename(inputDir, ext)
print "Based on the directory, I think the basename is " + firstBaseName

# test all the files in the directory
inputDir = inputDir.getAbsolutePath()
for root, directories, filenames in os.walk(inputDir):
	filenames.sort()
	for filename in filenames:
		print "Checking:",filename
		# Check for file extension
		if not filename.endswith(ext):
			continue
		imageInfo = parse_fileinfo(filename)
		baseName = imageInfo[0]
		wellName = imageInfo[1]
		posName = imageInfo[2]
		print "This is image " + baseName + ", well " + wellName + ", position "+ posName
