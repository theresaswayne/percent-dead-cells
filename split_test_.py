#@File(label = "Input file") inputImage

# test function for splitting

def parse_filename(filename):

	# takes a filename object returns a tuple of strings

	print "The filename is " + str(filename)
	fileString = str(filename)[:-4]

	print "The file name without extension is " + fileString 
	splitName = fileString.split("Scene") # should yield 2 components

	# TODO: the first component is the entire path. need to use the plain filename

	print "The first split gives " + str(splitName)
	
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


imageInfo = parse_filename(inputImage)
baseName = imageInfo[0]
wellName = imageInfo[1]
posName = imageInfo[2]
print "This is image " + baseName + ", well " +wellName+", position "+posName